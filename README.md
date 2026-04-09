# OCR Models Benchmark

This repository contains a reproducible benchmarking suite to evaluate different Optical Character Recognition (OCR) models and Vision-Language Models (VLMs) on an aggregated dataset of printed, scanned, and handwritten documents.

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python 3.11](https://img.shields.io/badge/python-3.11+-blue.svg)

## Project Structure

```text
ocr-benchmarks/
├── README.md                 # Project documentation
├── REPORT.md                 # Auto-generated benchmarking report
├── requirements.txt          # Minimal local dependencies
├── requirements-modal.txt    # Modal/GPU remote execution dependencies
├── shared.py                 # Core utilities (image loading, saving)
├── download_datasets.py      # Dataset fetching (FUNSD, XFUND, SROIE)
├── generate_pdfs.py          # Synthetic dataset builder
├── run_all.py                # Main orchestrator script
├── runners/                  # Individual model scripts
│   ├── run_easyocr.py
│   ├── run_glm_ocr.py
│   ├── run_paddleocr_vl.py
│   ├── run_qwen25_vl.py
│   └── run_olmocr2.py
├── metrics/                  # Evaluation logic
│   ├── cer.py
│   └── compare.py
├── test_documents/           # Test sets (scanned, handwritten, printed)
├── ground_truth/             # Reference text for test sets
└── results/                  # Auto-generated model outputs
```

## Evaluated Models

1. **EasyOCR** (Open-source traditional OCR)
2. **GLM-4V-9B** (Vision-Language Model via Modal GPU)
3. **PaddleOCR-VL** (PP-OCRv4 via Modal GPU)
4. **Qwen2.5-VL-7B-Instruct** (Vision-Language Model via Modal GPU)
5. **olmOCR-2** (allenai/olmOCR-7B-0225-preview via Modal GPU)

## Dataset Structure

The test suite consists of 16 sample documents:
- **Printed PDFs**: Mock receipts/invoices automatically generated for different languages (English, Spanish, French).
- **Scanned Forms**: From the FUNSD and XFUND datasets.
- **Scanned Receipts**: From the SROIE dataset.
- **Handwritten Samples**: Synthetic handwritten images.

## Setup and Installation

**1. Install Local Dependencies**
```bash
pip install -r requirements.txt
```

**2. Set up Modal (For GPU Models)**
The heavy VLMs (GLM-4V, Qwen2.5-VL, olmOCR-2) and PaddleOCR require a cloud GPU. This suite uses [Modal](https://modal.com) for serverless GPU execution.
```bash
pip install -r requirements-modal.txt
python -m modal setup
```
*(This will open a browser window to authenticate. You can use a free Modal account.)*

**3. Prepare the Dataset**
If you haven't downloaded the dataset yet, run the dataset preparation scripts:
```bash
python generate_pdfs.py      # Generates synthetic printed PDFs
python download_datasets.py  # Downloads SROIE, FUNSD, XFUND
```

## Running the Benchmarks

You can run individual models using their respective scripts in the `runners/` directory, or use the `run_all.py` orchestrator.

**Quick Start / Run everything:**
```bash
python run_all.py
```

**Run specific models:**
```bash
python run_all.py --models easyocr,glm_ocr
```

**Generate comparison report only (without re-evaluating):**
```bash
python run_all.py --compare
```

*(Add `--verbose` to any command for more detailed logging output).*

## Results & Reporting

The final evaluation metrics are aggregated and saved in:
- `results/comparison.json`
- `REPORT.md` (A human-readable markdown table summarizing the benchmark).

### Glossary of Metrics
- **CER (Character Error Rate):** Edit distance at character level. Lower is better (0.0 is perfect). Highly correlated with OCR quality.
- **WER (Word Error Rate):** Edit distance at word level. Lower is better.
- **Accuracy:** Computed as `max(0, 1 - CER)`. Higher is better.
- **F1 Score:** Harmonic mean of precision and recall at character level.
- **Median CER/WER:** Used alongside average to detect skewed model performance because OCR errors are often heavily tailed.

## Troubleshooting

- **`modal: command not found`**: Make sure your python bin path is configured, or run via `python -m modal setup`.
- **`WARNING: running in local fallback mode`**: A remote runner was executed but `modal` isn't installed. The script automatically inserts placeholders in `results/` so the final report can still generate.
- **`WARNING: PyMuPDF not installed...`**: Install via `pip install PyMuPDF` to allow `get_test_images()` to process the `printed/` directory.
