from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains import LLMChain
from langchain import PromptTemplate
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA

import os
from dotenv import load_dotenv

def read_items_from_file(file_path):
    """Read a list of items from a text file"""
    with open(file_path, 'r') as f:
        # Clean the items and return them as a list
        items = [line.strip() for line in f.readlines() if line.strip()]
    return items

def check_line_items_from_documents(claim_number):
    claim_number = "CLM000382"
    text_file_path = "list_of_items.txt"
    # load_dotenv(dotenv_path="C:/Users/abhishek221057/OneDrive - EXLService.com (I) Pvt. Ltd/Desktop/Agentic_bot/.env")    
    api_key = st.secrets["GROQ_API_KEY"]

    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")
    
    os.environ['HF_TOKEN']=st.secrets["HF_TOKEN"]

    embeddings=HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    llm=ChatGroq(groq_api_key=api_key,model_name="Llama3-8b-8192")

    prompt=ChatPromptTemplate.from_template(
        """
        Answer the questions based on the provided context only.
        Please provide the most accurate respone based on the question
        <context>
        {context}
        <context>
        Question:{input}

        """

    )

    loader=PyPDFLoader(claim_number+".pdf")
    docs=loader.load() 
    text_splitter=RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)
    final_documents=text_splitter.split_documents(docs) 
    vectors=FAISS.from_documents(final_documents,embeddings)

    text_file_items = read_items_from_file(text_file_path)

    document_chain=create_stuff_documents_chain(llm,prompt)
    retriever=vectors.as_retriever()
    retrieval_chain=create_retrieval_chain(retriever,document_chain)

    
    response=retrieval_chain.invoke({"context": final_documents, "input": "Provide a list of all the items mentioned in the invoice pdf.Only list items not anything else or any explanation and dont add number in front of item like if Engine is there then item will be Engine not 1. Engine. Dont include anything like this in response - here is the list of items mentioned in the invoice:"})
    # print(f'1------ {response['answer']}')
    invoice_items = response.get('answer', '').split('\n')
    # print(f'2-------{invoice_items}')
    # Clean and normalize both lists of items for comparison
    invoice_items = [item.strip().lower() for item in invoice_items if item.strip()]
    # print(f'3-------{invoice_items}')
    text_file_items = [item.strip().lower() for item in text_file_items]
    # print(f'4------{text_file_items}')
    # Find common items
    common_items = set(invoice_items).intersection(text_file_items)
    uncommon_items = set(invoice_items).difference(text_file_items)
    return list(common_items), list(uncommon_items)

# Example usage
# claim_number = "CLM000382"
# text_file_path = "list_of_items.txt"
# print(check_line_items_from_documents(claim_number, text_file_path))
