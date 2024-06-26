import os
from PyPDF2 import PdfReader
from es_client import es_client

def read_pdf(file_path):
    with open(file_path, 'rb') as file:
        pdf_reader = PdfReader(file)

        num_pages = len(pdf_reader.pages)

        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text()

    return text

directory_path = 'documents'

pdf_files = [f for f in os.listdir(directory_path) if f.endswith('.pdf')]

for pdf_file in pdf_files:
    file_path = os.path.join(directory_path, pdf_file)
    try:
        pdf_text = read_pdf(file_path)
        print(f'Text from {pdf_file}:\n{pdf_text}\n')
        data = {
            "text": pdf_text,
            "metadata": {
                "filename": pdf_file
            }
        }
        es_client.index(index="documents_ingestion", body=data)
    except Exception as e:
        print(f'Failed to read {pdf_file}: {e}')