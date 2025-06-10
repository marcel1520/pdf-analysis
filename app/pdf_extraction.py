import fitz

def extract_text_from_pdf(file_bytes) -> str:
    pdf = fitz.open(stream=file_bytes, filetype='pdf')
    full_text = ""
    for page in pdf:
        text = page.get_text().strip()
        full_text += text + "\n"
    pdf.close()
    return full_text.strip()