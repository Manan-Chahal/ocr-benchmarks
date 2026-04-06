"""
EasyOCR benchmark runner.
Runs EasyOCR on all test documents and saves results.
Can run locally (CPU) or on Modal (GPU).
"""

import json
import os
import sys
import time
import glob

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)


def get_test_images():
    """Collect all test document paths."""
    docs = []
    for subdir in ["scanned", "handwritten"]:
        folder = os.path.join(BASE, "test_documents", subdir)
        if os.path.exists(folder):
            for f in sorted(os.listdir(folder)):
                if f.lower().endswith((".png", ".jpg", ".jpeg", ".tiff", ".bmp")):
                    docs.append({
                        "path": os.path.join(folder, f),
                        "name": f,
                        "category": subdir,
                    })

    # For printed PDFs, convert to images first
    printed_dir = os.path.join(BASE, "test_documents", "printed")
    if os.path.exists(printed_dir):
        try:
            import fitz  # PyMuPDF
            for f in sorted(os.listdir(printed_dir)):
                if f.lower().endswith(".pdf"):
                    pdf_path = os.path.join(printed_dir, f)
                    doc = fitz.open(pdf_path)
                    for page_num in range(len(doc)):
                        page = doc[page_num]
                        pix = page.get_pixmap(dpi=200)
                        img_path = os.path.join(printed_dir, f"{os.path.splitext(f)[0]}_p{page_num}.png")
                        pix.save(img_path)
                        docs.append({
                            "path": img_path,
                            "name": os.path.splitext(f)[0],
                            "category": "printed",
                        })
                    doc.close()
        except ImportError:
            print("WARNING: PyMuPDF not installed, skipping PDF documents")

    return docs


def run_easyocr_benchmark():
    """Run EasyOCR on all test images."""
    try:
        import easyocr
    except ImportError:
        print("Installing easyocr...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "easyocr", "-q"])
        import easyocr

    # Initialize reader for all languages we test
    print("Initializing EasyOCR reader...")
    reader = easyocr.Reader(["en", "es", "fr"], gpu=True)

    docs = get_test_images()
    print(f"Found {len(docs)} test documents")

    results = {
        "model": "easyocr",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "documents": [],
    }

    for doc in docs:
        print(f"  Processing {doc['name']}...", end=" ", flush=True)
        start = time.time()

        try:
            raw_results = reader.readtext(doc["path"], detail=0, paragraph=True)
            ocr_text = "\n".join(raw_results)
            elapsed = time.time() - start
            print(f"OK ({elapsed:.2f}s, {len(ocr_text)} chars)")

            results["documents"].append({
                "name": doc["name"],
                "category": doc["category"],
                "ocr_text": ocr_text,
                "latency_s": round(elapsed, 3),
                "status": "success",
            })
        except Exception as e:
            elapsed = time.time() - start
            print(f"FAIL ({e})")
            results["documents"].append({
                "name": doc["name"],
                "category": doc["category"],
                "ocr_text": "",
                "latency_s": round(elapsed, 3),
                "status": f"error: {str(e)}",
            })

    # Save results
    out_path = os.path.join(RESULTS_DIR, "easyocr_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {out_path}")

    return results


if __name__ == "__main__":
    run_easyocr_benchmark()
