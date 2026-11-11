"""
JobShield AI - Document Extraction Module
Supports PyMuPDF (fitz) and PyPDF fallback for extracting text and metadata
from uploaded PDF offer letters and documents.
"""

import os
import re
from typing import Dict, Any, Tuple

try:
    import pymupdf as fitz  # Modern PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    try:
        import fitz
        HAS_PYMUPDF = True
    except ImportError:
        HAS_PYMUPDF = False

try:
    from pypdf import PdfReader
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False


def extract_text_from_pdf(file_path: str) -> Tuple[str, Dict[str, Any]]:
    """
    Extracts plain text and document metadata from a PDF file.
    Returns (extracted_text, metadata_dict).
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    text = ""
    metadata = {
        "pages": 0,
        "author": "",
        "creator": "",
        "producer": "",
        "title": "",
        "creation_date": "",
        "extractor_used": "none"
    }

    # Primary extractor: PyMuPDF (fitz)
    if HAS_PYMUPDF:
        try:
            doc = fitz.open(file_path)
            metadata["pages"] = len(doc)
            metadata["author"] = doc.metadata.get("author", "") or ""
            metadata["creator"] = doc.metadata.get("creator", "") or ""
            metadata["producer"] = doc.metadata.get("producer", "") or ""
            metadata["title"] = doc.metadata.get("title", "") or ""
            metadata["creation_date"] = str(doc.metadata.get("creationDate", "")) or ""
            metadata["extractor_used"] = "PyMuPDF"

            page_texts = []
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                page_texts.append(page.get_text())

            text = "\n".join(page_texts)
            doc.close()
        except Exception as e:
            text = ""

    # Fallback extractor: PyPDF
    if (not text or not text.strip()) and HAS_PYPDF:
        try:
            reader = PdfReader(file_path)
            metadata["pages"] = len(reader.pages)
            info = reader.metadata or {}
            metadata["author"] = str(info.get("/Author", ""))
            metadata["creator"] = str(info.get("/Creator", ""))
            metadata["producer"] = str(info.get("/Producer", ""))
            metadata["title"] = str(info.get("/Title", ""))
            metadata["extractor_used"] = "PyPDF"

            page_texts = []
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    page_texts.append(extracted)

            text = "\n".join(page_texts)
        except Exception as e:
            pass

    cleaned_text = clean_extracted_text(text)
    return cleaned_text, metadata


def extract_text_from_txt(file_path: str) -> Tuple[str, Dict[str, Any]]:
    """Extracts text from a plain .txt file with utf-8 or latin-1 encoding."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="latin-1", errors="ignore") as f:
            text = f.read()

    metadata = {
        "pages": 1,
        "author": "N/A",
        "creator": "Plain Text",
        "producer": "Plain Text File",
        "title": os.path.basename(file_path),
        "extractor_used": "Plain Text Reader"
    }
    return clean_extracted_text(text), metadata


def clean_extracted_text(raw_text: str) -> str:
    """Sanitizes text, normalizes linebreaks, collapses excess whitespace."""
    if not raw_text:
        return ""
    # Normalize unicode spaces and dashes
    text = raw_text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    # Remove excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def find_embedded_contacts(text: str) -> Dict[str, list]:
    """Finds emails, phone numbers, and URLs inside text."""
    emails = list(set(re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)))
    urls = list(set(re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', text)))
    # Generic Indian/Intl phone number pattern
    phones = list(set(re.findall(r'(?:\+?91[\-\s]?)?[6-9]\d{9}\b|\+?\d{1,3}[\-\s]?\d{3,4}[\-\s]?\d{3,4}', text)))
    
    return {
        "emails": emails[:5],
        "urls": urls[:5],
        "phones": phones[:5]
    }
