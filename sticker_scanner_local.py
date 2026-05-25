#!/usr/bin/env python3
"""
Sticker Scanner Local — Panini FIFA World Cup 2026
Utilise Ollama (modèle vision local) — aucune clé API requise.

Installation :
    pip install ollama
    ollama pull llama3.2-vision   # recommandé (~6 GB)
    ollama pull moondream2        # léger (~2 GB)

Usage :
    python sticker_scanner_local.py <dossier_photos>
    python sticker_scanner_local.py <dossier_photos> --model moondream2
    python sticker_scanner_local.py <dossier_photos> --output liste.txt
"""

import argparse
import base64
import sys
from pathlib import Path

try:
    import ollama
except ImportError:
    print("❌  Ollama non installé. Lance : pip install ollama", file=sys.stderr)
    sys.exit(1)

EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

PROMPT = (
    "This is a photo of one or more Panini FIFA World Cup 2026 stickers. "
    "Find ALL sticker codes visible. A code looks like 'MAR3', 'UZB3', 'FWC1', 'CRO1', etc. "
    "Reply with ONLY the codes separated by spaces (e.g. 'MAR3' or 'MAR3 UZB3'). "
    "If you cannot find any code, reply with 'UNKNOWN'."
)


def encode_image(path: Path) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def scan_image(path: Path, model: str) -> list[str]:
    image_b64 = encode_image(path)

    response = ollama.chat(
        model=model,
        messages=[
            {
                "role": "user",
                "content": PROMPT,
                "images": [image_b64],
            }
        ],
    )

    raw = response["message"]["content"].strip()
    if raw.upper() == "UNKNOWN" or not raw:
        return []
    tokens = [t.strip(".,;:") for t in raw.split() if t.replace("-", "").isalnum()]
    return tokens


def collect_images(folder: Path) -> list[Path]:
    images = []
    for ext in EXTENSIONS:
        images.extend(folder.glob(f"*{ext}"))
        images.extend(folder.glob(f"*{ext.upper()}"))
    return sorted(set(images))


def check_model(model: str) -> bool:
    try:
        models = [m["name"].split(":")[0] for m in ollama.list()["models"]]
        return model in models
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Scanne les photos de stickers Panini avec un modèle vision local (Ollama)"
    )
    parser.add_argument("dossier", help="Dossier contenant les photos")
    parser.add_argument(
        "--model", "-m",
        default="llama3.2-vision",
        help="Modèle Ollama à utiliser (défaut: llama3.2-vision)",
    )
    parser.add_argument(
        "--output", "-o",
        help="Fichier de sortie (défaut: affichage console)",
        default=None,
    )
    args = parser.parse_args()

    folder = Path(args.dossier)
    if not folder.exists() or not folder.is_dir():
        print(f"❌  Dossier introuvable : {folder}", file=sys.stderr)
        sys.exit(1)

    images = collect_images(folder)
    if not images:
        print(f"❌  Aucune image trouvée dans {folder}", file=sys.stderr)
        sys.exit(1)

    if not check_model(args.model):
        print(f"⚠️  Modèle '{args.model}' non trouvé localement.")
        print(f"   Lance : ollama pull {args.model}")
        sys.exit(1)

    print(f"🤖  Modèle  : {args.model}")
    print(f"📷  Photos  : {len(images)} fichier(s) dans {folder}")
    print("🔍  Analyse en cours...\n")

    all_numbers: list[str] = []
    unknown_files: list[str] = []

    for i, img_path in enumerate(images, 1):
        prefix = f"[{i:>3}/{len(images)}] {img_path.name:<40}"
        try:
            numbers = scan_image(img_path, args.model)
            if numbers:
                print(f"{prefix} → {' '.join(numbers)}")
                all_numbers.extend(numbers)
            else:
                print(f"{prefix} → ❓ non détecté")
                unknown_files.append(img_path.name)
        except Exception as e:
            print(f"{prefix} → ⚠️  erreur : {e}", file=sys.stderr)
            unknown_files.append(img_path.name)

    unique_numbers = sorted(
        set(all_numbers),
        key=lambda x: (x.rstrip("0123456789"), int(x[len(x.rstrip("0123456789")):] or 0)),
    )

    result_line = " ".join(unique_numbers)

    print(f"\n{'─' * 60}")
    print(f"✅  {len(unique_numbers)} numéro(s) unique(s) détecté(s)\n")

    if unknown_files:
        print(f"⚠️  {len(unknown_files)} photo(s) sans code détecté :")
        for f in unknown_files:
            print(f"     • {f}")
        print()

    print("📋  Liste pour LastSticker.com :")
    print("─" * 60)
    print(result_line)
    print("─" * 60)

    if args.output:
        Path(args.output).write_text(result_line + "\n", encoding="utf-8")
        print(f"\n💾  Sauvegardé dans : {args.output}")


if __name__ == "__main__":
    main()
