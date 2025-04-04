

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import numpy as np
import cv2
import pandas as pd
from mrl_passport import process_passport_information
from constant import *
from logger_config import logger
import uvicorn
from io import BytesIO
import Sure! Here's a comparative table listing **4 pros and cons** each for **PaddleOCR**, **DocTR**, and **Tesseract OCR**:

| OCR Engine     | Pros                                                                 | Cons                                                                 |
|----------------|----------------------------------------------------------------------|----------------------------------------------------------------------|
| **PaddleOCR**  | 1. High accuracy for multiple languages (including Japanese & Chinese).<br>2. Supports detection + recognition + layout.<br>3. Modular and customizable.<br>4. Active community and regular updates. | 1. Heavier models may require GPU for fast processing.<br>2. Slightly complex setup for beginners.<br>3. Less effective on low-resolution images.<br>4. Larger model size increases storage need. |
| **DocTR**      | 1. Built on PyTorch, easy to integrate with DL pipelines.<br>2. End-to-end OCR with detection + recognition.<br>3. Good performance on printed text.<br>4. Clean, modern API and documentation. | 1. Limited language support compared to PaddleOCR.<br>2. Struggles with handwriting.<br>3. Slower than PaddleOCR on large datasets.<br>4. Detection not as robust on distorted documents. |
| **Tesseract**  | 1. Lightweight and easy to set up.<br>2. No GPU required.<br>3. Good for printed English text.<br>4. Extensively documented, open-source. | 1. Poor accuracy on complex layouts and noisy backgrounds.<br>2. Weak support for non-Latin scripts.<br>3. No built-in detection (needs external box detection).<br>4. Slow on large files. |

Let me know if you want a PDF or Markdown export of this table, or a graphical chart version.
