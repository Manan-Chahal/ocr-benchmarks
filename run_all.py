"""
Main benchmark orchestrator.
Runs all 5 OCR models and generates the comparison report.
Usage:
    python run_all.py          # Run all models
    python run_all.py easyocr  # Run only EasyOCR
    python run_all.py compare  # Only run comparison (skip model runs)
"""

import os
import sys
import subprocess
import time

BASE = os.path.dirname(os.path.abspath(__file__))
RUNNERS = {
    "easyocr": os.path.join(BASE, "runners", "run_easyocr.py"),
    "glm_ocr": os.path.join(BASE, "runners", "run_glm_ocr.py"),
    "paddleocr_vl": os.path.join(BASE, "runners", "run_paddleocr_vl.py"),
    "qwen25_vl": os.path.join(BASE, "runners", "run_qwen25_vl.py"),
    "olmocr2": os.path.join(BASE, "runners", "run_olmocr2.py"),
}
COMPARE_SCRIPT = os.path.join(BASE, "metrics", "compare.py")


def run_model(name: str, script: str):
    """Run a single model benchmark."""
    print(f"\n{'='*60}")
    print(f"Running: {name}")
    print(f"{'='*60}")
    start = time.time()

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    result = subprocess.run(
        [sys.executable, script],
        cwd=BASE,
        env=env,
        capture_output=False,
    )

    elapsed = time.time() - start
    status = "OK" if result.returncode == 0 else f"FAILED (exit code {result.returncode})"
    print(f"\n{name}: {status} ({elapsed:.1f}s)")
    return result.returncode == 0


def main():
    args = sys.argv[1:]

    if "compare" in args:
        # Just run comparison
        print("Running comparison only...")
        subprocess.run([sys.executable, COMPARE_SCRIPT], cwd=BASE)
        return

    # Determine which models to run
    if args:
        models = {k: v for k, v in RUNNERS.items() if k in args}
        if not models:
            print(f"Unknown model(s): {args}")
            print(f"Available: {', '.join(RUNNERS.keys())}")
            sys.exit(1)
    else:
        models = RUNNERS

    print("=" * 60)
    print("OCR Benchmark Suite")
    print("=" * 60)
    print(f"Models to run: {', '.join(models.keys())}")
    print(f"Working directory: {BASE}")
    print()

    # Run each model
    success_count = 0
    for name, script in models.items():
        ok = run_model(name, script)
        if ok:
            success_count += 1

    print(f"\n{'='*60}")
    print(f"Completed: {success_count}/{len(models)} models ran successfully")
    print(f"{'='*60}")

    # Run comparison
    print("\nRunning comparison and generating report...")
    subprocess.run([sys.executable, COMPARE_SCRIPT], cwd=BASE)

    report_path = os.path.join(BASE, "REPORT.md")
    if os.path.exists(report_path):
        print(f"\nFinal report: {report_path}")


if __name__ == "__main__":
    main()
