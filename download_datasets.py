"""
Download sample images from SROIE, FUNSD datasets for OCR benchmarking.
Also generates handwritten-style sample images.
"""

import requests
import json
import os
import zipfile
import io

BASE = os.path.dirname(os.path.abspath(__file__))
SCANNED = os.path.join(BASE, "test_documents", "scanned")
HANDWRITTEN = os.path.join(BASE, "test_documents", "handwritten")
GT = os.path.join(BASE, "ground_truth")

os.makedirs(SCANNED, exist_ok=True)
os.makedirs(HANDWRITTEN, exist_ok=True)
os.makedirs(GT, exist_ok=True)

# ────────────────────────────────────────────────────────────────────────────
# SROIE — English Receipts (files are 000.jpg, 001.jpg, etc.)
# ────────────────────────────────────────────────────────────────────────────

SROIE_BASE = "https://raw.githubusercontent.com/zzzDavid/ICDAR-2019-SROIE/master/data"

SROIE_SAMPLES = ["000", "001", "002", "003", "004"]

def download_sroie():
    print("\nDownloading SROIE receipt images...")
    for i, fid in enumerate(SROIE_SAMPLES, 1):
        img_url = f"{SROIE_BASE}/img/{fid}.jpg"
        txt_url = f"{SROIE_BASE}/box/{fid}.txt"

        out_img = os.path.join(SCANNED, f"en_receipt_{i:03d}.jpg")
        out_gt = os.path.join(GT, f"en_receipt_{i:03d}.txt")

        # Download image
        print(f"  Downloading {fid}.jpg...", end=" ", flush=True)
        r = requests.get(img_url, timeout=30)
        if r.status_code == 200:
            with open(out_img, "wb") as f:
                f.write(r.content)
            print("OK image", end=" ")
        else:
            print(f"FAIL image ({r.status_code})", end=" ")
            continue

        # Download ground truth & extract text only
        r2 = requests.get(txt_url, timeout=30)
        if r2.status_code == 200:
            texts = []
            for line in r2.text.strip().split("\n"):
                parts = line.strip().split(",", 8)
                if len(parts) >= 9:
                    texts.append(parts[8])
                elif len(parts) == 1 and parts[0].strip():
                    texts.append(parts[0])
            with open(out_gt, "w", encoding="utf-8") as f:
                f.write("\n".join(texts))
            print("OK ground truth")
        else:
            print(f"FAIL ground truth ({r2.status_code})")


# ────────────────────────────────────────────────────────────────────────────
# FUNSD — English scanned forms
# ────────────────────────────────────────────────────────────────────────────

FUNSD_URL = "https://guillaumejaume.github.io/FUNSD/dataset.zip"

def download_funsd():
    print("\nDownloading FUNSD form images...")
    print("  Downloading dataset.zip (~16 MB)...", end=" ", flush=True)

    r = requests.get(FUNSD_URL, timeout=120)
    if r.status_code != 200:
        print(f"FAIL ({r.status_code})")
        print("  Try downloading manually from: https://guillaumejaume.github.io/FUNSD/")
        return

    print("OK")
    print("  Extracting...", end=" ", flush=True)

    z = zipfile.ZipFile(io.BytesIO(r.content))

    # Find image files in testing_data
    image_files = sorted([
        n for n in z.namelist()
        if "testing_data/images/" in n and n.endswith(".png")
    ])

    annotation_files = sorted([
        n for n in z.namelist()
        if "testing_data/annotations/" in n and n.endswith(".json")
    ])

    print(f"found {len(image_files)} test images")

    # Take 5 samples
    for i, img_path in enumerate(image_files[:5], 1):
        out_img = os.path.join(SCANNED, f"en_form_{i:03d}.png")
        with open(out_img, "wb") as f:
            f.write(z.read(img_path))
        print(f"  OK en_form_{i:03d}.png")

        # Find matching annotation
        basename = os.path.basename(img_path).replace(".png", ".json")
        matching = [a for a in annotation_files if a.endswith(basename)]
        if matching:
            raw_bytes = z.read(matching[0])
            # Try multiple encodings
            content = None
            for enc in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
                try:
                    content = raw_bytes.decode(enc)
                    break
                except (UnicodeDecodeError, Exception):
                    continue
            if content is None:
                # Last resort: decode ignoring errors
                content = raw_bytes.decode("utf-8", errors="ignore")

            try:
                ann_data = json.loads(content)
                texts = []
                for item in ann_data.get("form", []):
                    if item.get("text", "").strip():
                        texts.append(item["text"])
                out_gt = os.path.join(GT, f"en_form_{i:03d}.txt")
                with open(out_gt, "w", encoding="utf-8") as f:
                    f.write("\n".join(texts))
                print(f"    OK ground truth ({len(texts)} text segments)")
            except json.JSONDecodeError as e:
                print(f"    FAIL ground truth parse: {e}")

    z.close()


# ────────────────────────────────────────────────────────────────────────────
# XFUND — Multilingual scanned forms (es, fr, zh, ja)
# ────────────────────────────────────────────────────────────────────────────

def download_xfund():
    print("\nDownloading XFUND multilingual ground truth...")

    # XFUND annotation JSONs from HuggingFace
    HF_BASE = "https://huggingface.co/datasets/fixie-ai/xfund/resolve/main"
    langs = {"es": "es.val.json", "fr": "fr.val.json", "zh": "zh.val.json", "ja": "ja.val.json"}

    for lang, json_file in langs.items():
        url = f"{HF_BASE}/{json_file}"
        print(f"  Downloading {lang} annotations...", end=" ", flush=True)
        r = requests.get(url, timeout=60)
        if r.status_code != 200:
            # Try alternative
            url2 = f"https://raw.githubusercontent.com/nickmuchi/HuggingFaceDatasets/main/XFUND/{json_file}"
            r = requests.get(url2, timeout=60)
            if r.status_code != 200:
                print(f"FAIL ({r.status_code}) - skipping")
                # Create placeholder ground truth
                out_gt = os.path.join(GT, f"{lang}_form_001.txt")
                placeholder_texts = {
                    "es": "Nombre\nDireccion\nTelefono\nFecha\nFirma",
                    "fr": "Nom\nAdresse\nTelephone\nDate\nSignature",
                    "zh": "name\naddress\ntelephone\ndate",
                    "ja": "name\naddress\ntelephone\ndate",
                }
                with open(out_gt, "w", encoding="utf-8") as f:
                    f.write(placeholder_texts.get(lang, "text"))
                print(f"    Created placeholder ground truth for {lang}")
                continue

        print("OK")

        # XFUND is JSONL format
        lines = r.text.strip().split("\n")
        for idx, line in enumerate(lines[:1], 1):
            try:
                doc = json.loads(line)
            except json.JSONDecodeError:
                print(f"  FAIL parse {lang} line {idx}")
                continue

            # Try to download the image
            img_info = doc.get("img", {})
            if isinstance(img_info, dict):
                img_fname = img_info.get("fname", "")
            else:
                img_fname = ""

            downloaded_img = False
            if img_fname:
                # Try downloading from HF
                for base_url in [
                    f"{HF_BASE}/{img_fname}",
                    f"https://raw.githubusercontent.com/nickmuchi/HuggingFaceDatasets/main/XFUND/{img_fname}",
                ]:
                    r2 = requests.get(base_url, timeout=30)
                    if r2.status_code == 200 and len(r2.content) > 1000:
                        out_img = os.path.join(SCANNED, f"{lang}_form_{idx:03d}.jpg")
                        with open(out_img, "wb") as f:
                            f.write(r2.content)
                        print(f"    OK {lang}_form_{idx:03d}.jpg")
                        downloaded_img = True
                        break

            if not downloaded_img:
                print(f"    Image not available for {lang} - ground truth only")

            # Extract ground truth
            texts = []
            for item in doc.get("document", []):
                if item.get("text", "").strip():
                    texts.append(item["text"])

            out_gt = os.path.join(GT, f"{lang}_form_{idx:03d}.txt")
            with open(out_gt, "w", encoding="utf-8") as f:
                f.write("\n".join(texts))
            print(f"    OK ground truth: {len(texts)} text segments")


# ────────────────────────────────────────────────────────────────────────────
# Handwritten — Generate synthetic samples
# ────────────────────────────────────────────────────────────────────────────

def create_handwritten_samples():
    from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
    import random

    print("\nCreating synthetic handwritten-style samples...")

    samples = [
        {
            "name": "en_iam_001",
            "text": "The quick brown fox jumps over the lazy dog.\nPack my box with five dozen liquor jugs.\nHow vexingly quick daft zebras jump."
        },
        {
            "name": "en_iam_002",
            "text": "Dear Professor Henderson,\nI am writing to request an extension\non the research paper deadline.\nThe laboratory results are still pending\nand I need additional time to complete\nthe analysis. Thank you for your\nconsideration.\nSincerely, James Mitchell"
        },
        {
            "name": "en_iam_003",
            "text": "Meeting Notes - March 15, 2026\nAttendees: Smith, Johnson, Williams\nAgenda:\n1. Budget review for Q2\n2. New hiring plan\n3. Project timeline update\nAction items:\n- Submit revised budget by Friday\n- Schedule interviews for next week"
        },
    ]

    for sample in samples:
        img = Image.new("L", (800, 600), 240)
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("arial.ttf", 22)
        except Exception:
            font = ImageFont.load_default()

        y = 40
        for line in sample["text"].split("\n"):
            x = 30 + random.randint(-5, 10)
            y += random.randint(-2, 4)
            draw.text((x, y), line, fill=random.randint(10, 50), font=font)
            y += 38 + random.randint(-3, 5)

        img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
        img_rgb = ImageOps.colorize(img, black=(20, 15, 40), white=(245, 240, 235))

        out_path = os.path.join(HANDWRITTEN, f"{sample['name']}.png")
        img_rgb.save(out_path)
        print(f"  OK {sample['name']}.png")

        gt_path = os.path.join(GT, f"{sample['name']}.txt")
        with open(gt_path, "w", encoding="utf-8") as f:
            f.write(sample["text"])
        print(f"    OK ground truth")


# ────────────────────────────────────────────────────────────────────────────
# Main
# ────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("OCR Benchmark - Dataset Downloader")
    print("=" * 60)

    download_sroie()
    download_funsd()
    download_xfund()
    create_handwritten_samples()

    print("\n" + "=" * 60)
    print("Dataset preparation complete!")
    print("=" * 60)

    scanned_count = len([f for f in os.listdir(SCANNED) if os.path.isfile(os.path.join(SCANNED, f))])
    hw_count = len([f for f in os.listdir(HANDWRITTEN) if os.path.isfile(os.path.join(HANDWRITTEN, f))])
    gt_count = len([f for f in os.listdir(GT) if os.path.isfile(os.path.join(GT, f))])

    print(f"\nScanned images:    {scanned_count} files")
    print(f"Handwritten images: {hw_count} files")
    print(f"Ground truth files: {gt_count} files")
