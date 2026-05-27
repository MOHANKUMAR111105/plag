import docx2txt
from PyPDF2 import PdfReader

ALLOWED_MIMETYPES = [
    "text/plain",
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
]

def read_file(file):
    """Reads content from a file and returns it as text."""
    content = ""
    if file is None:
        return content

    if file.mimetype == "text/plain":
        content = file.read().decode("utf-8")

    elif file.mimetype == "application/pdf":
        try:
            pdf_reader = PdfReader(file)
            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted:
                    content += extracted
        except Exception as e:
            print(f"PDF read error: {e}")

    elif file.mimetype == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        try:
            content = docx2txt.process(file)
        except Exception as e:
            print(f"DOCX read error: {e}")

    return content.strip()
