from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from utils import db


def process_files(files):
    text = ""
    for file in files:
        pdf = PdfReader(file)
        for page in pdf.pages:
            text += page.extract_text()
    return text


def create_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n", chunk_size=1500, chunk_overlap=300, length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks


def save_document_metadata(filename, content, file_hash):
    document_data = {
        "filename": filename,
        "content": content,
        "hash": file_hash,
    }
    db.documents_collection.insert_one(document_data)


def document_exists(file_hash):
    return db.documents_collection.find_one({"hash": file_hash}) is not None
