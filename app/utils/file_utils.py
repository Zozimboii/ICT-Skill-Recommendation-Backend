# app/utils/file_utils.py
import os

import pdfplumber

_upload_env = os.getenv("UPLOAD_DIR")
if _upload_env:
    UPLOAD_DIR = os.path.abspath(_upload_env)
else:
    BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")


def save_file(file):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    return file_path


def extract_text_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text