from flask import Flask, request, Response, stream_with_context
from flask_cors import CORS
from flask_allowedhosts import limit_hosts
from query import rag_chain
from es_client import create_es_client
from constants import *
import os
from dotenv import load_dotenv
from boto3 import client
from langchain_openai import OpenAIEmbeddings
from langchain_experimental.text_splitter import SemanticChunker
from langchain_chroma import Chroma

load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key, model="text-embedding-3-large")
text_splitter = SemanticChunker(
    embeddings, 
    breakpoint_threshold_type="gradient",
)

def get_client():
    return client(
        's3',
        'us-east-1',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    )
def read_pdf(file_path):
    with open(file_path, 'rb') as file:
        pdf_reader = PdfReader(file)
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text()
        file.close()
    return text

app = Flask(__name__)
CORS(app)

def on_denied():
    return "Unauthorized access", 401

@app.route('/ask', methods=['POST'])
@limit_hosts(allowed_hosts=ALLOWED_HOSTS, on_denied=on_denied)
def ask():
    data = request.get_json()
    question = data.get('prompt')
    def generate():
        useful_links = []
        for result in rag_chain.stream({ "input": question },  {'configurable': {'session_id': 1}}):
            if 'context' in result:
                for doc in result['context']:
                    metadata = doc.metadata
                    if 'filename' in metadata:
                        useful_links.append(metadata['filename'])
            if 'answer' in result:
                yield result['answer']

        if len(useful_links) > 0:
            yield "\n\n"
            yield '<strong> Useful links are </strong> : \n'
            for link in useful_links:
                yield '<a href="#">' + link + '</a>'
                yield '\n'
    return Response(stream_with_context(generate()), mimetype='application/json')

@app.route('/generate_embeddings', methods=['GET'])
@limit_hosts(allowed_hosts=ALLOWED_HOSTS, on_denied=on_denied)
def generate_embeddings():
    document_uid = request.args.get('document_uid')

    with tempfile.NamedTemporaryFile(delete=False) as temp:
        temp.write(document_uid.encode())
        temp_name = temp.name
        s3_client = get_client()
        try:
            s3_client.download_file(os.getenv('DMS_S3_BUCKET'), document_uid, temp_name)
            pdf_text = read_pdf(temp_name)
            docs = text_splitter.create_documents([pdf_text])
            documents = []
            for doc in docs:
                doc.metadata = metadata
                documents.append(doc)
            Chroma.from_documents(
                documents,
                embeddings,
                persist_directory="./vectorstore",
            )
        except Exception as e:
            return str(e), 500
        finally:
            os.unlink(temp_name)
    return "Embeddings generated successfully"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)