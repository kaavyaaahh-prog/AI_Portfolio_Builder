"""
pdf_parser.py
--------------
Uses PyMuPDF (imported as `fitz`) to pull plain text out of an
uploaded resume PDF so it can be sent to the AI model.
"""

import fitz  # PyMuPDF


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Opens a PDF file on disk and returns all the text inside it
    as one big string (page by page).
    """
    extracted_text = ""

    try:
        document = fitz.open(pdf_path)
        for page in document:
            extracted_text += page.get_text()
        document.close()
    except Exception as e:
        print(f"[PDF Parser Error] Could not read PDF: {e}")
        return ""

    return extracted_text.strip()
