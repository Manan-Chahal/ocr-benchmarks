# OCR Models Benchmark

This repository contains a reproducible benchmarking suite to evaluate different Optical Character Recognition (OCR) models and Vision-Language Models (VLMs) on an aggregated dataset of printed, scanned, and handwritten documents.

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

1. **Install Local Dependencies**
   ```bash
   pip install easyocr PyMuPDF reportlab Pillow requests python-Levenshtein
   ```

2. **Set up Modal (For GPU Models)**
   The heavy VLMs (GLM-4V, Qwen2.5-VL, olmOCR-2) and PaddleOCR require a cloud GPU. This suite uses [Modal](https://modal.com) for serverless GPU execution.
   ```bash
   pip install modal
   python -m modal setup
   ```
   *(This will open a browser window to authenticate. You can use a free Modal account.)*

3. **Prepare the Dataset**
   If you haven't downloaded the dataset yet, run the dataset preparation scripts:
   ```bash
   python generate_pdfs.py      # Generates synthetic printed PDFs
   python download_datasets.py  # Downloads SROIE, FUNSD, XFUND
   ```

## Running the Benchmarks

You can run individual models using their respective scripts in the `runners/` directory, or use the `run_all.py` orchestrator.

**Run a single model:**
```bash
python runners/run_easyocr.py
```

**Run everything:**
```bash
python run_all.py
```

**Generate comparison report only (without re-evaluating):**
```bash
python run_all.py compare
```

## Results & Reporting
The final evaluation metrics, including Character Error Rate (CER), Word Error Rate (WER), character-level Accuracy, and processing Latency, are aggregated and saved in:
- `results/comparison.json`
- `REPORT.md` (A human-readable markdown table summarizing the benchmark).
