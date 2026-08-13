import os
import pymupdf
from docx import Document


def read_text_file(file_path):

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def read_pdf_file(file_path):

    pdf = pymupdf.open(file_path)

    pages = []

    for page in pdf:
        pages.append(page.get_text())

    pdf.close()

    return "\n\n".join(pages)


def read_docx_file(file_path):

    document = Document(file_path)

    paragraphs = []

    for paragraph in document.paragraphs:

        text = paragraph.text.strip()

        if text:
            paragraphs.append(text)

    return "\n\n".join(paragraphs)


def read_file(file_path):

    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".pdf":

        return read_pdf_file(file_path)

    if extension == ".docx":

        return read_docx_file(file_path)

    return read_text_file(file_path)