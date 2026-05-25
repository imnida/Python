#!/usr/bin/env python3
"""
Sticker Scanner Local — Panini FIFA World Cup 2026
Utilise Ollama (modèle vision local) — aucune clé API requise.
Génère 3 listes pour LastSticker.com : collection, manquants, doubles.

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
from collections import Counter
from pathlib import Path

try:
    import ollama
except ImportError:
    print("❌  Ollama non installé. Lance : pip install ollama", file=sys.stderr)
    sys.exit(1)

# Liste complète de l'album FIFA World Cup 2026 (LastSticker.com)
ALBUM = [
    "00",
    "FWC1","FWC2","FWC3","FWC4","FWC5","FWC6","FWC7","FWC8",
    "MEX1","MEX2","MEX3","MEX4","MEX5","MEX6","MEX7","MEX8","MEX9","MEX10",
    "MEX11","MEX12","MEX13","MEX14","MEX15","MEX16","MEX17","MEX18","MEX19","MEX20",
    "RSA1","RSA2","RSA3","RSA4","RSA5","RSA6","RSA7","RSA8","RSA9","RSA10",
    "RSA11","RSA12","RSA13","RSA14","RSA15","RSA16","RSA17","RSA18","RSA19","RSA20",
    "KOR1","KOR2","KOR3","KOR4","KOR5","KOR6","KOR7","KOR8","KOR9","KOR10",
    "KOR11","KOR12","KOR13","KOR14","KOR15","KOR16","KOR17","KOR18","KOR19","KOR20",
    "CZE1","CZE2","CZE3","CZE4","CZE5","CZE6","CZE7","CZE8","CZE9","CZE10",
    "CZE11","CZE12","CZE13","CZE14","CZE15","CZE16","CZE17","CZE18","CZE19","CZE20",
    "CAN1","CAN2","CAN3","CAN4","CAN5","CAN6","CAN7","CAN8","CAN9","CAN10",
    "CAN11","CAN12","CAN13","CAN14","CAN15","CAN16","CAN17","CAN18","CAN19","CAN20",
    "BIH1","BIH2","BIH3","BIH4","BIH5","BIH6","BIH7","BIH8","BIH9","BIH10",
    "BIH11","BIH12","BIH13","BIH14","BIH15","BIH16","BIH17","BIH18","BIH19","BIH20",
    "QAT1","QAT2","QAT3","QAT4","QAT5","QAT6","QAT7","QAT8","QAT9","QAT10",
    "QAT11","QAT12","QAT13","QAT14","QAT15","QAT16","QAT17","QAT18","QAT19","QAT20",
    "SUI1","SUI2","SUI3","SUI4","SUI5","SUI6","SUI7","SUI8","SUI9","SUI10",
    "SUI11","SUI12","SUI13","SUI14","SUI15","SUI16","SUI17","SUI18","SUI19","SUI20",
    "BRA1","BRA2","BRA3","BRA4","BRA5","BRA6","BRA7","BRA8","BRA9","BRA10",
    "BRA11","BRA12","BRA13","BRA14","BRA15","BRA16","BRA17","BRA18","BRA19","BRA20",
    "MAR1","MAR2","MAR3","MAR4","MAR5","MAR6","MAR7","MAR8","MAR9","MAR10",
    "MAR11","MAR12","MAR13","MAR14","MAR15","MAR16","MAR17","MAR18","MAR19","MAR20",
    "HAI1","HAI2","HAI3","HAI4","HAI5","HAI6","HAI7","HAI8","HAI9","HAI10",
    "HAI11","HAI12","HAI13","HAI14","HAI15","HAI16","HAI17","HAI18","HAI19","HAI20",
    "SCO1","SCO2","SCO3","SCO4","SCO5","SCO6","SCO7","SCO8","SCO9","SCO10",
    "SCO11","SCO12","SCO13","SCO14","SCO15","SCO16","SCO17","SCO18","SCO19","SCO20",
    "USA1","USA2","USA3","USA4","USA5","USA6","USA7","USA8","USA9","USA10",
    "USA11","USA12","USA13","USA14","USA15","USA16","USA17","USA18","USA19","USA20",
    "PAR1","PAR2","PAR3","PAR4","PAR5","PAR6","PAR7","PAR8","PAR9","PAR10",
    "PAR11","PAR12","PAR13","PAR14","PAR15","PAR16","PAR17","PAR18","PAR19","PAR20",
    "AUS1","AUS2","AUS3","AUS4","AUS5","AUS6","AUS7","AUS8","AUS9","AUS10",
    "AUS11","AUS12","AUS13","AUS14","AUS15","AUS16","AUS17","AUS18","AUS19","AUS20",
    "TUR1","TUR2","TUR3","TUR4","TUR5","TUR6","TUR7","TUR8","TUR9","TUR10",
    "TUR11","TUR12","TUR13","TUR14","TUR15","TUR16","TUR17","TUR18","TUR19","TUR20",
    "GER1","GER2","GER3","GER4","GER5","GER6","GER7","GER8","GER9","GER10",
    "GER11","GER12","GER13","GER14","GER15","GER16","GER17","GER18","GER19","GER20",
    "GER2s","GER3s","GER4s","GER5s","GER6s","GER7s","GER8s","GER9s","GER10s",
    "GER11s","GER12s","GER14s","GER15s","GER16s","GER17s","GER18s","GER19s","GER20s",
    "CUW1","CUW2","CUW3","CUW4","CUW5","CUW6","CUW7","CUW8","CUW9","CUW10",
    "CUW11","CUW12","CUW13","CUW14","CUW15","CUW16","CUW17","CUW18","CUW19","CUW20",
    "CIV1","CIV2","CIV3","CIV4","CIV5","CIV6","CIV7","CIV8","CIV9","CIV10",
    "CIV11","CIV12","CIV13","CIV14","CIV15","CIV16","CIV17","CIV18","CIV19","CIV20",
    "ECU1","ECU2","ECU3","ECU4","ECU5","ECU6","ECU7","ECU8","ECU9","ECU10",
    "ECU11","ECU12","ECU13","ECU14","ECU15","ECU16","ECU17","ECU18","ECU19","ECU20",
    "NED1","NED2","NED3","NED4","NED5","NED6","NED7","NED8","NED9","NED10",
    "NED11","NED12","NED13","NED14","NED15","NED16","NED17","NED18","NED19","NED20",
    "JPN1","JPN2","JPN3","JPN4","JPN5","JPN6","JPN7","JPN8","JPN9","JPN10",
    "JPN11","JPN12","JPN13","JPN14","JPN15","JPN16","JPN17","JPN18","JPN19","JPN20",
    "SWE1","SWE2","SWE3","SWE4","SWE5","SWE6","SWE7","SWE8","SWE9","SWE10",
    "SWE11","SWE12","SWE13","SWE14","SWE15","SWE16","SWE17","SWE18","SWE19","SWE20",
    "TUN1","TUN2","TUN3","TUN4","TUN5","TUN6","TUN7","TUN8","TUN9","TUN10",
    "TUN11","TUN12","TUN13","TUN14","TUN15","TUN16","TUN17","TUN18","TUN19","TUN20",
    "BEL1","BEL2","BEL3","BEL4","BEL5","BEL6","BEL7","BEL8","BEL9","BEL10",
    "BEL11","BEL12","BEL13","BEL14","BEL15","BEL16","BEL17","BEL18","BEL19","BEL20",
    "BEL2s","BEL3s","BEL4s","BEL5s","BEL6s","BEL7s","BEL8s","BEL9s","BEL10s",
    "BEL11s","BEL12s","BEL14s","BEL15s","BEL16s","BEL17s","BEL18s","BEL19s","BEL20s",
    "EGY1","EGY2","EGY3","EGY4","EGY5","EGY6","EGY7","EGY8","EGY9","EGY10",
    "EGY11","EGY12","EGY13","EGY14","EGY15","EGY16","EGY17","EGY18","EGY19","EGY20",
    "IRN1","IRN2","IRN3","IRN4","IRN5","IRN6","IRN7","IRN8","IRN9","IRN10",
    "IRN11","IRN12","IRN13","IRN14","IRN15","IRN16","IRN17","IRN18","IRN19","IRN20",
    "NZL1","NZL2","NZL3","NZL4","NZL5","NZL6","NZL7","NZL8","NZL9","NZL10",
    "NZL11","NZL12","NZL13","NZL14","NZL15","NZL16","NZL17","NZL18","NZL19","NZL20",
    "ESP1","ESP2","ESP3","ESP4","ESP5","ESP6","ESP7","ESP8","ESP9","ESP10",
    "ESP11","ESP12","ESP13","ESP14","ESP15","ESP16","ESP17","ESP18","ESP19","ESP20",
    "CPV1","CPV2","CPV3","CPV4","CPV5","CPV6","CPV7","CPV8","CPV9","CPV10",
    "CPV11","CPV12","CPV13","CPV14","CPV15","CPV16","CPV17","CPV18","CPV19","CPV20",
    "KSA1","KSA2","KSA3","KSA4","KSA5","KSA6","KSA7","KSA8","KSA9","KSA10",
    "KSA11","KSA12","KSA13","KSA14","KSA15","KSA16","KSA17","KSA18","KSA19","KSA20",
    "URU1","URU2","URU3","URU4","URU5","URU6","URU7","URU8","URU9","URU10",
    "URU11","URU12","URU13","URU14","URU15","URU16","URU17","URU18","URU19","URU20",
    "FRA1","FRA2","FRA3","FRA4","FRA5","FRA6","FRA7","FRA8","FRA9","FRA10",
    "FRA11","FRA12","FRA13","FRA14","FRA15","FRA16","FRA17","FRA18","FRA19","FRA20",
    "FRA2s","FRA3s","FRA4s","FRA5s","FRA6s","FRA7s","FRA8s","FRA9s","FRA10s",
    "FRA11s","FRA12s","FRA14s","FRA15s","FRA16s","FRA17s","FRA18s","FRA19s","FRA20s",
    "SEN1","SEN2","SEN3","SEN4","SEN5","SEN6","SEN7","SEN8","SEN9","SEN10",
    "SEN11","SEN12","SEN13","SEN14","SEN15","SEN16","SEN17","SEN18","SEN19","SEN20",
    "IRQ1","IRQ2","IRQ3","IRQ4","IRQ5","IRQ6","IRQ7","IRQ8","IRQ9","IRQ10",
    "IRQ11","IRQ12","IRQ13","IRQ14","IRQ15","IRQ16","IRQ17","IRQ18","IRQ19","IRQ20",
    "NOR1","NOR2","NOR3","NOR4","NOR5","NOR6","NOR7","NOR8","NOR9","NOR10",
    "NOR11","NOR12","NOR13","NOR14","NOR15","NOR16","NOR17","NOR18","NOR19","NOR20",
    "ARG1","ARG2","ARG3","ARG4","ARG5","ARG6","ARG7","ARG8","ARG9","ARG10",
    "ARG11","ARG12","ARG13","ARG14","ARG15","ARG16","ARG17","ARG18","ARG19","ARG20",
    "ALG1","ALG2","ALG3","ALG4","ALG5","ALG6","ALG7","ALG8","ALG9","ALG10",
    "ALG11","ALG12","ALG13","ALG14","ALG15","ALG16","ALG17","ALG18","ALG19","ALG20",
    "AUT1","AUT2","AUT3","AUT4","AUT5","AUT6","AUT7","AUT8","AUT9","AUT10",
    "AUT11","AUT12","AUT13","AUT14","AUT15","AUT16","AUT17","AUT18","AUT19","AUT20",
    "JOR1","JOR2","JOR3","JOR4","JOR5","JOR6","JOR7","JOR8","JOR9","JOR10",
    "JOR11","JOR12","JOR13","JOR14","JOR15","JOR16","JOR17","JOR18","JOR19","JOR20",
    "POR1","POR2","POR3","POR4","POR5","POR6","POR7","POR8","POR9","POR10",
    "POR11","POR12","POR13","POR14","POR15","POR16","POR17","POR18","POR19","POR20",
    "COD1","COD2","COD3","COD4","COD5","COD6","COD7","COD8","COD9","COD10",
    "COD11","COD12","COD13","COD14","COD15","COD16","COD17","COD18","COD19","COD20",
    "UZB1","UZB2","UZB3","UZB4","UZB5","UZB6","UZB7","UZB8","UZB9","UZB10",
    "UZB11","UZB12","UZB13","UZB14","UZB15","UZB16","UZB17","UZB18","UZB19","UZB20",
    "COL1","COL2","COL3","COL4","COL5","COL6","COL7","COL8","COL9","COL10",
    "COL11","COL12","COL13","COL14","COL15","COL16","COL17","COL18","COL19","COL20",
    "ENG1","ENG2","ENG3","ENG4","ENG5","ENG6","ENG7","ENG8","ENG9","ENG10",
    "ENG11","ENG12","ENG13","ENG14","ENG15","ENG16","ENG17","ENG18","ENG19","ENG20",
    "CRO1","CRO2","CRO3","CRO4","CRO5","CRO6","CRO7","CRO8","CRO9","CRO10",
    "CRO11","CRO12","CRO13","CRO14","CRO15","CRO16","CRO17","CRO18","CRO19","CRO20",
    "GHA1","GHA2","GHA3","GHA4","GHA5","GHA6","GHA7","GHA8","GHA9","GHA10",
    "GHA11","GHA12","GHA13","GHA14","GHA15","GHA16","GHA17","GHA18","GHA19","GHA20",
    "PAN1","PAN2","PAN3","PAN4","PAN5","PAN6","PAN7","PAN8","PAN9","PAN10",
    "PAN11","PAN12","PAN13","PAN14","PAN15","PAN16","PAN17","PAN18","PAN19","PAN20",
    "FWC9","FWC10","FWC11","FWC12","FWC13","FWC14","FWC15","FWC16","FWC17","FWC18","FWC19",
    "CC-US1","CC-US2","CC-US3","CC-US4","CC-US5","CC-US6",
    "CC-US7","CC-US8","CC-US9","CC-US10","CC-US11","CC-US12",
    "CC-LAM1","CC-LAM2","CC-LAM3","CC-LAM4","CC-LAM5","CC-LAM6","CC-LAM7",
    "CC-LAM8","CC-LAM9","CC-LAM10","CC-LAM11","CC-LAM12","CC-LAM13","CC-LAM14",
    "CC-RW1","CC-RW2","CC-RW3","CC-RW4","CC-RW5","CC-RW6","CC-RW7",
    "CC-RW8","CC-RW9","CC-RW10","CC-RW11","CC-RW12","CC-RW13","CC-RW14",
    "CC-EU1","CC-EU2","CC-EU3","CC-EU4","CC-EU5","CC-EU6",
    "CC-EU7","CC-EU8","CC-EU9","CC-EU10","CC-EU11","CC-EU12",
    "ARG13mc","AUS13mc","BEL13mc","BRA13mc","CAN13mc","CIV13mc","COL13mc",
    "CRO13mc","ECU13mc","ENG13mc","ESP13mc","FRA13mc","GER13mc","GHA13mc",
    "JPN13mc","KOR13mc","RSA13mc","MAR13mc","MEX13mc","NED13mc","NOR13mc",
    "PAN13mc","QAT13mc","SEN13mc","SUI13mc","TUN13mc","URU13mc","USA13mc","UZB13mc",
    "LM","JD","VJ","AD","LD","LMO","MC","MS","JB","KM","FW","RJ",
    "AH","EH","CG","CR","HS","LY","CP","FV",
    "LM-b","JD-b","VJ-b","AD-b","LD-b","LMO-b","MC-b","MS-b","JB-b","KM-b",
    "FW-b","RJ-b","AH-b","EH-b","CG-b","CR-b","HS-b","LY-b","CP-b","FV-b",
    "LM-s","JD-s","VJ-s","AD-s","LD-s","LMO-s","MC-s","MS-s","JB-s","KM-s",
    "FW-s","RJ-s","AH-s","EH-s","CG-s","CR-s","HS-s","LY-s","CP-s","FV-s",
    "LM-g","JD-g","VJ-g","AD-g","LD-g","LMO-g","MC-g","MS-g","JB-g","KM-g",
    "FW-g","RJ-g","AH-g","EH-g","CG-g","CR-g","HS-g","LY-g","CP-g","FV-g",
]

ALBUM_SET = set(ALBUM)

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
        messages=[{"role": "user", "content": PROMPT, "images": [image_b64]}],
    )
    raw = response["message"]["content"].strip()
    if raw.upper() == "UNKNOWN" or not raw:
        return []
    return [t.strip(".,;:") for t in raw.split() if t.replace("-", "").isalnum()]


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


def album_sort_key(code: str) -> tuple:
    try:
        return (ALBUM.index(code),)
    except ValueError:
        return (len(ALBUM), code)


def build_three_lists(counter: Counter) -> tuple[list, list, list]:
    collection = [c for c in ALBUM if counter[c] >= 1]
    missing    = [c for c in ALBUM if counter[c] == 0]
    doubles    = []
    for c in ALBUM:
        if counter[c] >= 2:
            doubles.extend([c] * (counter[c] - 1))
    return collection, missing, doubles


def print_section(title: str, items: list[str]) -> str:
    line = " ".join(items)
    sep = "─" * 60
    print(f"\n{sep}")
    print(f"📋  {title} ({len(items)}) :")
    print(sep)
    print(line if line else "(vide)")
    return line


def main():
    parser = argparse.ArgumentParser(
        description="Scanne les photos de stickers Panini — génère 3 listes LastSticker.com"
    )
    parser.add_argument("dossier", help="Dossier contenant les photos")
    parser.add_argument("--model", "-m", default="llama3.2-vision",
                        help="Modèle Ollama (défaut: llama3.2-vision)")
    parser.add_argument("--output", "-o", default=None,
                        help="Fichier de sortie .txt (défaut: console uniquement)")
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
        print(f"⚠️  Modèle '{args.model}' non trouvé. Lance : ollama pull {args.model}")
        sys.exit(1)

    print(f"🤖  Modèle  : {args.model}")
    print(f"📷  Photos  : {len(images)} fichier(s)")
    print("🔍  Analyse en cours...\n")

    counter: Counter = Counter()
    unknown_files: list[str] = []

    for i, img_path in enumerate(images, 1):
        prefix = f"[{i:>3}/{len(images)}] {img_path.name:<40}"
        try:
            codes = scan_image(img_path, args.model)
            valid = [c for c in codes if c in ALBUM_SET]
            invalid = [c for c in codes if c not in ALBUM_SET]
            if valid:
                counter.update(valid)
                note = " ".join(valid)
                if invalid:
                    note += f"  (ignorés: {' '.join(invalid)})"
                print(f"{prefix} → {note}")
            else:
                print(f"{prefix} → ❓ non détecté")
                unknown_files.append(img_path.name)
        except Exception as e:
            print(f"{prefix} → ⚠️  erreur : {e}", file=sys.stderr)
            unknown_files.append(img_path.name)

    if unknown_files:
        print(f"\n⚠️  {len(unknown_files)} photo(s) sans code reconnu :")
        for f in unknown_files:
            print(f"     • {f}")

    collection, missing, doubles = build_three_lists(counter)

    l1 = print_section("Ma collection", collection)
    l2 = print_section("Les autocollants manquants", missing)
    l3 = print_section("Mes autocollants en double", doubles)
    print(f"\n{'─' * 60}")
    print(f"   Collection : {len(collection)} / {len(ALBUM)}")
    print(f"   Manquants  : {len(missing)}")
    print(f"   Doubles    : {len(doubles)}")

    if args.output:
        out = Path(args.output)
        out.write_text(
            f"MA COLLECTION\n{l1}\n\n"
            f"MANQUANTS\n{l2}\n\n"
            f"DOUBLES\n{l3}\n",
            encoding="utf-8",
        )
        print(f"\n💾  Sauvegardé dans : {args.output}")


if __name__ == "__main__":
    main()
