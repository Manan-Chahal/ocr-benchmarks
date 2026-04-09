# OCR Model Benchmark Report

**Date:** 2026-04-09
**Tested by:** Auto-Orchestrator
**GPU:** T4/A10G on Modal
**Test set:** 16 documents (3 printed, 10 scanned, 3 handwritten)

## Summary

| Model | Avg CER | Avg WER | Table Acc. | Speed (s/doc) | Bbox? | Notes |
|-------|---------|---------|------------|---------------|-------|-------|
| easyocr | 0.2172 | 0.4958 | [Scored Manually] | 8.059 | Yes | |
| glm_ocr | 0.2192 | 0.3163 | [Scored Manually] | 18.347 | No | |
| paddleocr_vl | 0.1714 | 0.4269 | [Scored Manually] | 2.664 | Yes | |
| qwen25_vl | 0.1312 | 0.2058 | [Scored Manually] | 13.196 | No | |
| olmocr2 | 0.5656 | 0.8745 | [Scored Manually] | 18.822 | No | |

## Detailed Results by Document

### en_form_001.png
- **easyocr**: CER = 0.2944
- **glm_ocr**: CER = 0.1680
- **paddleocr_vl**: CER = 0.2699
- **qwen25_vl**: CER = 0.1465
- **olmocr2**: CER = 0.3123

### en_form_002.png
- **easyocr**: CER = 0.6024
- **glm_ocr**: CER = 0.9473
- **paddleocr_vl**: CER = 0.5940
- **qwen25_vl**: CER = 0.5305
- **olmocr2**: CER = 0.7246

### en_form_003.png
- **easyocr**: CER = 0.2823
- **glm_ocr**: CER = 0.1562
- **paddleocr_vl**: CER = 0.1719
- **qwen25_vl**: CER = 0.1554
- **olmocr2**: CER = 0.2440

### en_form_004.png
- **easyocr**: CER = 0.2724
- **glm_ocr**: CER = 0.2889
- **paddleocr_vl**: CER = 0.2017
- **qwen25_vl**: CER = 0.2205
- **olmocr2**: CER = 0.3002

### en_form_005.png
- **easyocr**: CER = 0.4153
- **glm_ocr**: CER = 1.2264
- **paddleocr_vl**: CER = 0.4513
- **qwen25_vl**: CER = 0.3853
- **olmocr2**: CER = 3.4228

### en_receipt_001.jpg
- **easyocr**: CER = 0.2557
- **glm_ocr**: CER = 0.0639
- **paddleocr_vl**: CER = 0.1175
- **qwen25_vl**: CER = 0.0763
- **olmocr2**: CER = 0.6412

### en_receipt_002.jpg
- **easyocr**: CER = 0.2690
- **glm_ocr**: CER = 0.1988
- **paddleocr_vl**: CER = 0.2120
- **qwen25_vl**: CER = 0.1082
- **olmocr2**: CER = 0.5073

### en_receipt_003.jpg
- **easyocr**: CER = 0.1272
- **glm_ocr**: CER = 0.0028
- **paddleocr_vl**: CER = 0.0816
- **qwen25_vl**: CER = 0.0124
- **olmocr2**: CER = 0.7248

### en_receipt_004.jpg
- **easyocr**: CER = 0.2277
- **glm_ocr**: CER = 0.0942
- **paddleocr_vl**: CER = 0.1250
- **qwen25_vl**: CER = 0.0771
- **olmocr2**: CER = 0.6301

### en_receipt_005.jpg
- **easyocr**: CER = 0.2999
- **glm_ocr**: CER = 0.0251
- **paddleocr_vl**: CER = 0.1205
- **qwen25_vl**: CER = 0.0326
- **olmocr2**: CER = 0.6110

### en_iam_001.png
- **easyocr**: CER = 0.0164
- **glm_ocr**: CER = 0.0000
- **paddleocr_vl**: CER = 0.0164
- **qwen25_vl**: CER = 0.0000
- **olmocr2**: CER = 0.0000

### en_iam_002.png
- **easyocr**: CER = 0.0282
- **glm_ocr**: CER = 0.0000
- **paddleocr_vl**: CER = 0.0121
- **qwen25_vl**: CER = 0.0000
- **olmocr2**: CER = 0.0000

### en_iam_003.png
- **easyocr**: CER = 0.0263
- **glm_ocr**: CER = 0.0000
- **paddleocr_vl**: CER = 0.0088
- **qwen25_vl**: CER = 0.0000
- **olmocr2**: CER = 0.0000

### en_payroll_register
- **easyocr**: CER = 0.1657
- **glm_ocr**: CER = 0.1078
- **paddleocr_vl**: CER = 0.1564
- **qwen25_vl**: CER = 0.1448
- **olmocr2**: CER = 0.3499

### es_factura
- **easyocr**: CER = 0.0576
- **glm_ocr**: CER = 0.1002
- **paddleocr_vl**: CER = 0.0650
- **qwen25_vl**: CER = 0.0991
- **olmocr2**: CER = 0.3124

### fr_rapport_medical
- **easyocr**: CER = 0.1349
- **glm_ocr**: CER = 0.1276
- **paddleocr_vl**: CER = 0.1376
- **qwen25_vl**: CER = 0.1103
- **olmocr2**: CER = 0.2689

## Recommendation

Based on the results, we recommend:
- **Primary OCR model:** `qwen25_vl` because it achieved the highest character-level accuracy.
- **Bounding box model:** `paddleocr` or `easyocr` because they natively emit bounding box coordinates.
- **Combination strategy:** We recommend using EasyOCR/PaddleOCR solely to find dense text regions (bboxes), then cropping those regions and passing them to Qwen2.5-VL for highly accurate transcription.

## Appendix: Raw Output Samples
### easyocr
*(See `results/` folder for individual `_output.txt` files)*

### glm_ocr
*(See `results/` folder for individual `_output.txt` files)*

### paddleocr_vl
*(See `results/` folder for individual `_output.txt` files)*

### qwen25_vl
*(See `results/` folder for individual `_output.txt` files)*

### olmocr2
*(See `results/` folder for individual `_output.txt` files)*
