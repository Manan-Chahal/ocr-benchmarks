"""
Main benchmark orchestrator.
Runs OCR models and generates the comparison report.

Usage:
    python run_all.py            # Run all models
    python run_all.py --models easyocr,glm_ocr
    python run_all.py --compare  # Only generate report (skip model runs)
    python run_all.py --verbose
"""

import argparse
import os
import sys
import subprocess
import time

BASE = os.path.dirname(os.path.abspath(__file__))
# Note: we import get_logger from shared
sys.path.insert(0, BASE)
from shared import get_logger

log = get_logger("runner")

AVAILABLE_RUNNERS = {
    "easyocr": os.path.join(BASE, "runners", "run_easyocr.py"),
    "glm_ocr": os.path.join(BASE, "runners", "run_glm_ocr.py"),
    "paddleocr_vl": os.path.join(BASE, "runners", "run_paddleocr_vl.py"),
    "qwen25_vl": os.path.join(BASE, "runners", "run_qwen25_vl.py"),
    "olmocr2": os.path.join(BASE, "runners", "run_olmocr2.py"),
}
COMPARE_SCRIPT = os.path.join(BASE, "metrics", "compare.py")


def run_model(name: str, script: str) -> bool:
    """Run a single model benchmark and return success status."""
    log.info("\n" + "="*60)
    log.info("Running script: %s", name)
    log.info("="*60)
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
    success = result.returncode == 0
    status = "OK" if success else f"FAILED (exit code {result.returncode})"
    log.info("\n%s: %s (%.1fs)", name, status, elapsed)
    return success


def main():
    parser = argparse.ArgumentParser(description="OCR Benchmark Suite")
    parser.add_argument(
        "--models", type=str, default="all",
        help="Comma-separated list of models to run, or 'all'"
    )
    parser.add_argument(
        "--compare", action="store_true",
        help="Only run comparison/report generation"
    )
    parser.add_argument(
         "--verbose", action="store_true",
         help="Enable verbose output"
    )
    args = parser.parse_args()

    if args.verbose:
         import logging
         log.setLevel(logging.DEBUG)

    if args.compare:
        log.info("Running comparison only...")
        subprocess.run([sys.executable, COMPARE_SCRIPT], cwd=BASE)
        return

    # Determine which models to run
    models_to_run = {}
    if args.models.lower() == "all":
        models_to_run = AVAILABLE_RUNNERS
    else:
        requested = [m.strip() for m in args.models.split(",")]
        for m in requested:
            if m in AVAILABLE_RUNNERS:
                models_to_run[m] = AVAILABLE_RUNNERS[m]
            else:
                log.error("Unknown model: %s. Available: %s", m, list(AVAILABLE_RUNNERS.keys()))
                sys.exit(1)

    log.info("=" * 60)
    log.info("OCR Benchmark Suite")
    log.info("=" * 60)
    log.info("Models to run: %s", ", ".join(models_to_run.keys()))
    log.info("Working directory: %s\n", BASE)

    # Run each model
    results_summary = []
    success_count = 0
    for name, script in models_to_run.items():
        ok = run_model(name, script)
        results_summary.append((name, "Success" if ok else "Failed"))
        if ok:
            success_count += 1

    log.info("\n" + "="*60)
    log.info("Run Summary:")
    for name, status in results_summary:
         log.info("  %s: %s", name, status)
    log.info("Completed: %d/%d models ran successfully", success_count, len(models_to_run))
    log.info("="*60)

    # Run comparison
    log.info("\nGenerating report...")
    subprocess.run([sys.executable, COMPARE_SCRIPT], cwd=BASE)

    report_path = os.path.join(BASE, "REPORT.md")
    if os.path.exists(report_path):
        log.info("\nFinished! See %s", report_path)


if __name__ == "__main__":
    main()
