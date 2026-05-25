#!/usr/bin/env python3
"""
Sticker Scanner — Panini FIFA World Cup 2026
Analyse des photos de stickers et génère la liste pour LastSticker.com
Usage: python sticker_scanner.py <dossier_photos> [--output fichier.txt]
"""

import anthropic
import argparse
import base64
import sys
from pathlib import Path

EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
MEDIA_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".gif": "image/gif",
}

PROMPT = (
    "This is a photo of one or more Panini FIFA World Cup 2026 stickers. "
    "Look carefully at each sticker and identify ALL sticker numbers visible. "
    "Reply with ONLY the numbers separated by spaces (e.g. '42' or '42 87 103'). "
    "If you cannot find any number, reply with 'UNKNOWN'."
)


def encode_image(path: Path) -> tuple[str, str]:
    ext = path.suffix.lower()
    with open(path, "rb") as f:
        data = base64.standard_b64encode(f.read()).decode("utf-8")
    return data, MEDIA_TYPES.get(ext, "image/jpeg")


def scan_image(client: anthropic.Anthropic, path: Path) -> list[str]:
    image_data, media_type = encode_image(path)

    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=256,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        },
                    },
                    {"type": "text", "text": PROMPT},
                ],
            }
        ],
    )

    raw = response.content[0].text.strip()
    if raw.upper() == "UNKNOWN" or not raw:
        return []
    # Keep only tokens that look like numbers (pure digits or alphanumeric codes like "FWC12")
    tokens = [t for t in raw.split() if t.replace("-", "").isalnum()]
    return tokens


def collect_images(folder: Path) -> list[Path]:
    images = []
    for ext in EXTENSIONS:
        images.extend(folder.glob(f"*{ext}"))
        images.extend(folder.glob(f"*{ext.upper()}"))
    return sorted(set(images))


def main():
    parser = argparse.ArgumentParser(
        description="Scanne les photos de stickers Panini et génère la liste pour LastSticker.com"
    )
    parser.add_argument("dossier", help="Dossier contenant les photos")
    parser.add_argument(
        "--output", "-o", help="Fichier de sortie (défaut: affichage console)", default=None
    )
    args = parser.parse_args()

    folder = Path(args.dossier)
    if not folder.exists() or not folder.is_dir():
        print(f"Erreur : dossier introuvable → {folder}", file=sys.stderr)
        sys.exit(1)

    images = collect_images(folder)
    if not images:
        print(f"Aucune image trouvée dans {folder}", file=sys.stderr)
        sys.exit(1)

    print(f"📷  {len(images)} photo(s) trouvée(s) dans {folder}")
    print("🔍  Analyse en cours...\n")

    client = anthropic.Anthropic()
    all_numbers: list[str] = []
    unknown_files: list[str] = []

    for i, img_path in enumerate(images, 1):
        prefix = f"[{i:>3}/{len(images)}] {img_path.name:<40}"
        try:
            numbers = scan_image(client, img_path)
            if numbers:
                print(f"{prefix} → {' '.join(numbers)}")
                all_numbers.extend(numbers)
            else:
                print(f"{prefix} → ❓ non détecté")
                unknown_files.append(img_path.name)
        except Exception as e:
            print(f"{prefix} → ⚠️  erreur : {e}", file=sys.stderr)
            unknown_files.append(img_path.name)

    # Dédoublonnage et tri numérique si possible
    unique_numbers = sorted(
        set(all_numbers),
        key=lambda x: int(x) if x.isdigit() else x,
    )

    result_line = " ".join(unique_numbers)

    print(f"\n{'─' * 60}")
    print(f"✅  {len(unique_numbers)} numéro(s) unique(s) détecté(s)\n")

    if unknown_files:
        print(f"⚠️  {len(unknown_files)} photo(s) sans numéro détecté :")
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
