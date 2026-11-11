"""
JobShield AI - Sample PDF Generator
Generates sample PDF offer letters for testing the PDF upload feature.
"""

import os
try:
    import pymupdf as fitz  # Modern PyMuPDF
except ImportError:
    import fitz
from samples import SAMPLE_OFFERS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_DIR = os.path.join(BASE_DIR, "test_samples")
os.makedirs(SAMPLE_DIR, exist_ok=True)

def create_sample_pdf(filename: str, title: str, text: str):
    doc = fitz.open()
    page = doc.new_page(width=595, height=842) # A4 size

    # Header banner
    page.draw_rect(fitz.Rect(40, 40, 555, 90), color=(0.1, 0.2, 0.5), fill=(0.95, 0.96, 1.0))
    page.insert_text(fitz.Point(55, 65), title, fontsize=14, color=(0.1, 0.2, 0.5))
    page.insert_text(fitz.Point(55, 80), "OFFICIAL DOCUMENT / RECRUITMENT RECORD", fontsize=9, color=(0.4, 0.4, 0.4))

    # Body text
    lines = text.strip().split("\n")
    y = 120
    for line in lines:
        if y > 790:
            page = doc.new_page(width=595, height=842)
            y = 60
        
        fontsize = 10
        color = (0.8, 0.1, 0.1) if ("DEPOSIT" in line.upper() or "REFUNDABLE" in line.upper() or "UPI" in line.upper()) else (0.1, 0.1, 0.1)
        
        # Word wrap line if too long
        if len(line) > 80:
            words = line.split(" ")
            chunk = ""
            for w in words:
                if len(chunk) + len(w) + 1 > 80:
                    page.insert_text(fitz.Point(50, y), chunk, fontsize=fontsize, color=color)
                    y += 14
                    chunk = w
                else:
                    chunk = (chunk + " " + w).strip()
            if chunk:
                page.insert_text(fitz.Point(50, y), chunk, fontsize=fontsize, color=color)
                y += 16
        else:
            page.insert_text(fitz.Point(50, y), line, fontsize=fontsize, color=color)
            y += 16

    # Footer
    page.draw_line(fitz.Point(40, 800), fitz.Point(555, 800), color=(0.8, 0.8, 0.8), width=1)
    page.insert_text(fitz.Point(50, 815), "Generated for JobShield AI Recruitment Safety Assessment Demonstration", fontsize=8, color=(0.5, 0.5, 0.5))

    out_path = os.path.join(SAMPLE_DIR, filename)
    doc.save(out_path)
    doc.close()
    print(f"Created: {out_path}")

if __name__ == "__main__":
    create_sample_pdf(
        "sample_scam_offer.pdf",
        "APEX GLOBAL TECHNOLOGIES - OFFER LETTER",
        SAMPLE_OFFERS["scam_upfront_fee"]["text"]
    )
    create_sample_pdf(
        "sample_legit_offer.pdf",
        "INNOVATELABS SOLUTIONS - INTERNSHIP OFFER",
        SAMPLE_OFFERS["legitimate_internship"]["text"]
    )
    print("All sample PDFs generated successfully.")
