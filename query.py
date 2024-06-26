from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, OpenAI, ChatOpenAI
from dotenv import load_dotenv
from langchain_openai import OpenAI
import os
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')

embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key, model="text-embedding-3-large")

vectordb = Chroma(persist_directory="./vectorstore", embedding_function=embeddings)
retriever = vectordb.as_retriever(search_type='similarity', search_kargs={'k': 1})

llm = ChatOpenAI(model="gpt-4-turbo", openai_api_key=openai_api_key)

prompt_template = PromptTemplate.from_template("""                              
Mechanical, Electrical, and Plumbing (MEP) Engineering Question Answering System, maintenance related questions.                  
Context: {context}
Question: {question}
""")

rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt_template
    | llm
    | StrOutputParser()
)

while True:
   question = input("Ask a question: ")
   result = rag_chain.invoke(question)
   print("Answer", result)

