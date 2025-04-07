import pytesseract
from pdf2image import convert_from_path
import streamlit as st
from PIL import Image
import re
import os

# ---------- Functions ----------
def extract_invoice_data_fixed(raw_text):
    data = {}
    invoice_match = re.search(r'INV[-\s]?(\w+)', raw_text)
    data['invoice_no'] = f"INV-{invoice_match.group(1)}" if invoice_match else None
    date_match = re.search(r'Date[:\-]?\s*([A-Za-z]+\s\d{1,2},\s\d{4})', raw_text)
    data['date'] = date_match.group(1) if date_match else None
    tax_match = re.search(r'Total Tax[:\-]?\s*\$([0-9.,]+)', raw_text)
    data['total_tax'] = tax_match.group(1) if tax_match else None
    total_match = re.search(r'Total\s+\$([0-9.,]+)', raw_text)
    data['total_amount'] = total_match.group(1) if total_match else None
    item_lines = re.findall(r'(Product\s*\d+)\s+(\d+)\s+\$([0-9.,]+)', raw_text)
    items = [{'name': i[0], 'qty': int(i[1]), 'price': float(i[2])} for i in item_lines]
    data['items'] = items
    return data

def pdf_to_text(pdf_file):
    images = convert_from_path(pdf_file)
    text = ""
    for page in images:
        text += pytesseract.image_to_string(page)
    return text

# ---------- Streamlit UI ----------
st.set_page_config(page_title="Invoice Scanner", layout="centered")
st.title("🧾 Invoice OCR Scanner")

uploaded_file = st.file_uploader("Upload PDF Invoice", type=["pdf"])

if uploaded_file is not None:
    with open("uploaded_invoice.pdf", "wb") as f:
        f.write(uploaded_file.read())

    st.info("🔍 Extracting text with OCR...")
    raw_text = pdf_to_text("uploaded_invoice.pdf")

    st.subheader("📋 Raw Text")
    st.text(raw_text)

    st.subheader("📊 Extracted Invoice Data")
    extracted = extract_invoice_data_fixed(raw_text)
    st.json(extracted)
