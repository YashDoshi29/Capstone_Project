import pytesseract
from pdf2image import convert_from_bytes

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    images = convert_from_bytes(pdf_bytes)
    text = "\n".join([pytesseract.image_to_string(img, config="--psm 6") for img in images])
    return text
