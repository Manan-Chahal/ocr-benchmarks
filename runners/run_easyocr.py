"""
EasyOCR benchmark runner.
Runs EasyOCR on all test documents and saves results.
Can run locally (CPU) or on GPU if available.
"""

import sys
import os
import time

# Add parent dir to path so we can import shared
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared import get_test_images, save_results, get_logger

log = get_logger("easyocr")


def run_easyocr_benchmark():
    """Run EasyOCR on all test images."""
    try:
        import easyocr
    except ImportError:
        log.info("Installing easyocr...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "easyocr", "-q"])
        import easyocr

    log.info("Initialising EasyOCR reader (en, es, fr)...")
    reader = easyocr.Reader(["en", "es", "fr"], gpu=True)

    docs = get_test_images(as_bytes=False)
    log.info("Found %d test documents", len(docs))

    results = []
    for doc in docs:
        log.info("  Processing %s...", doc["name"])
        start = time.time()
        try:
            # detail=1 gives List of [bounding_box, text, confidence]
            raw_results = reader.readtext(doc["path"], detail=1)
            
            texts = []
            bboxes = []
            for box, text, conf in raw_results:
                 texts.append(text)
                 # box is usually a list of 4 points: [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                 # convert numpy Ints to native Python ints so JSON serialises properly
                 bboxes.append([[int(p[0]), int(p[1])] for p in box])
                 
            ocr_text = "\n".join(texts)
            elapsed = time.time() - start
            log.info("    OK (%.2fs, %d chars)", elapsed, len(ocr_text))
            
            results.append({
                "name": doc["name"],
                "category": doc["category"],
                "ocr_text": ocr_text,
                "bounding_boxes": bboxes,
                "latency_s": round(elapsed, 3),
                "status": "success",
            })
        except Exception as e:
            elapsed = time.time() - start
            log.error("    FAIL: %s", e)
            results.append({
                "name": doc["name"],
                "category": doc["category"],
                "ocr_text": "",
                "bounding_boxes": None,
                "latency_s": round(elapsed, 3),
                "status": f"error: {str(e)}",
            })

    save_results("easyocr", results)
    return results


if __name__ == "__main__":
    run_easyocr_benchmark()
