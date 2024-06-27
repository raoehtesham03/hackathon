from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, OpenAI, ChatOpenAI
from dotenv import load_dotenv
import os
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.chains import create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain

load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')

embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key, model="text-embedding-3-large")

vectordb = Chroma(persist_directory="./vectorstore", embedding_function=embeddings)
retriever = vectordb.as_retriever(search_type='similarity', search_kargs={'k': 1})
create_history_aware_retriever


llm = ChatOpenAI(model="gpt-4-turbo", openai_api_key=openai_api_key)

### Contextualize question ###
contextualize_q_system_prompt = (
    "Mechanical, Electrical, and Plumbing (MEP) systems related questions are only answered."
)

contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

history_aware_retriever = create_history_aware_retriever(
    llm, retriever, contextualize_q_prompt,
)

### Answer question ###
system_prompt = (
    "Mechanical, Electrical, and Plumbing (MEP) systems related questions are only answered."
    "\n\n"
    "{context}"
)

qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

init_rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
rag_chain = RunnableWithMessageHistory(
    init_rag_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
)
