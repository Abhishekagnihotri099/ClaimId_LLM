from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document

from langchain.chains import LLMChain
from langchain import PromptTemplate
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA

import os
from dotenv import load_dotenv

def check_notes_incident_description(note_body):
    # Load environment variables (e.g., Groq API keys)
    load_dotenv(dotenv_path="C:/Users/abhishek221057/OneDrive - EXLService.com (I) Pvt. Ltd/Desktop/Agentic_bot/.env")    
    api_key = st.secrets["GROQ_API_KEY"]

    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")

    # Step 1: Create a Document object
    doc = Document(page_content=note_body, metadata={"source": "example", "author": "LangChain Docs"})
    
    # Step 2: Split the document into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=30)
    docs = text_splitter.split_documents([doc])

    # Step 3: Use FAISS for chunk embeddings and retrieval
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")  # Embedding model for vectorization
    db = FAISS.from_documents(docs, embeddings)

    # Step 4: Define the query and create RetrievalQA
    query = (
        "Analyze the following text and determine whether it describes an accident incident. "
        "If it does, return a structured JSON object with the following fields: "
        "{"
        "  'incident_detected': true, "
        "  'incident_type': '<Type of Accident>', "
        "  'time': '<Time of Incident>', "
        "  'location': '<Location of Incident>', "
        "  'parties_involved': ['<Party 1>', '<Party 2>', '...'], "
        "  'summary': '<Brief Summary of the Incident>' "
        "} "
        "If it does not describe an accident or you cannot determine if it describes an incident then just return a structured JSON object with the following fields and this json should be a valid json ehich dont give jsondecodeerror and dont have any unwanted linespaces and prefixes and spaces and dont return anything else, dont need any explanation for the response: "
        "{"
        "  'incident_detected': true "
        "} "
    )

    llm = ChatGroq(groq_api_key=api_key, model="gemma2-9b-it")
    retriever = db.as_retriever()
    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

    # Step 5: Get the response from the LLM
    try:
        response = qa_chain.run(query)
        return response
    except Exception as e:
        print(f"Error while processing the query: {e}")
        return {"incident_detected": False}
