import pdfplumber
import io

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Takes raw PDF bytes, extracts all text from every page,
    returns one big string. This string is what gets sent to Gemini.
    """
    pages = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:   # some pages are blank or image-only
                pages.append(text)

    full_text = '\n'.join(pages)

    # Basic cleanup — remove excessive blank lines
    lines = [line for line in full_text.splitlines() if line.strip()]
    return '\n'.join(lines)