from __future__ import annotations

import os
from typing import Callable

import pdfplumber
from docx import Document


def _read_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def _read_docx(path: str) -> str:
    doc = Document(path)
    parts = []
    for p in doc.paragraphs:
        text = p.text.strip()
        if text:
            parts.append(text)
    return "\n".join(parts)


def _read_pdf(path: str) -> str:
    parts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            text = text.strip()
            if text:
                parts.append(text)
    return "\n".join(parts)


def parse_resume(path: str) -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Resume file not found: {path}")

    ext = os.path.splitext(path)[1].lower()
    readers: dict[str, Callable[[str], str]] = {
        ".txt": _read_text_file,
        ".md": _read_text_file,
        ".docx": _read_docx,
        ".pdf": _read_pdf,
    }

    if ext not in readers:
        raise ValueError(f"Unsupported resume format: {ext}")

    return readers[ext](path)


def parse_jd(jd_input: str) -> str:
    if os.path.exists(jd_input):
        ext = os.path.splitext(jd_input)[1].lower()
        if ext in {".txt", ".md"}:
            return _read_text_file(jd_input)
        if ext == ".docx":
            return _read_docx(jd_input)
        if ext == ".pdf":
            return _read_pdf(jd_input)
        raise ValueError(f"Unsupported JD format: {ext}")
    return jd_input
