import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from es_client import es_client
from langchain_experimental.text_splitter import SemanticChunker
from langchain_chroma import Chroma

load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')

embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key, model="text-embedding-3-large")

text_splitter = SemanticChunker(
    embeddings, 
    breakpoint_threshold_type="gradient",
)

response = es_client.search(index="documents_ingestion", body={"query": {"match_all": {}}})

documents = []

for hit in response['hits']['hits']:
    source = hit['_source']
    page_content = source.get('text', '')
    metadata = source.get('metadata', {})

    docs = text_splitter.create_documents([page_content])
    for doc in docs:
        doc.metadata = metadata
        documents.append(doc)

vectorstore = Chroma.from_documents(
    documents,
    embeddings,
    persist_directory="./vectorstore",
)