import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from es_client import create_es_client
from langchain_experimental.text_splitter import SemanticChunker
from langchain_chroma import Chroma

load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
HOST='https://hackthon_user:redhat123@hood-production.es.us-east-1.aws.found.io'

# embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key, model="text-embedding-3-large")

# text_splitter = SemanticChunker(
#     embeddings, 
#     breakpoint_threshold_type="gradient",
# )

response = create_es_client(HOST).search(index="assets", body={"query": {"match_all": {}}})

print(response)
# documents = []

# for hit in response['hits']['hits']:
#     source = hit['_source']
#     page_content = source.get('text', '')
#     metadata = source.get('metadata', {})

#     docs = text_splitter.create_documents([page_content])
#     for doc in docs:
#         doc.metadata = metadata
#         documents.append(doc)

# vectorstore = Chroma.from_documents(
#     documents,
#     embeddings,
#     persist_directory="./vectorstore",
# )