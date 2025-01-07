## RAG Q&A Conversation With PDF Including Chat History
import streamlit as st
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

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
# load_dotenv()


# embeddings=HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def chatbot_response(data):
    comments_str = data.get('comments', '')
    final_output = data.get('final_output', '')
    
    # Combine comments into a single string
    # comments_str = ' '.join(comments)
    
    # Combine comments string with final output
    combined_str = f"This is complete context of my flow-{comments_str} and hence the final output is {final_output}"
    ## set up Streamlit 
    st.header("Conversational Q&A ChatBot")
    # load_dotenv(dotenv_path="C:/Users/abhishek221057/OneDrive - EXLService.com (I) Pvt. Ltd/Desktop/Agentic_bot/.env")    
    api_key = st.secrets["GROQ_API_KEY"]
    os.environ['HF_TOKEN']=st.secrets["HF_TOKEN"]

    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")

    llm=ChatGroq(groq_api_key=api_key,model_name="Gemma2-9b-It")

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

    doc = Document(page_content=combined_str, metadata={"source": "example", "author": "LangChain Docs"})
        
    # Step 2: Split the document into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=30)
    docs = text_splitter.split_documents([doc])

    # Step 3: Use FAISS for chunk embeddings and retrieval
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")  # Embedding model for vectorization
    db = FAISS.from_documents(docs, embeddings)
    retriever = db.as_retriever()

    user_prompt=st.text_input("Enter your query from the above flow followed by claim number")

    if user_prompt:
        document_chain=create_stuff_documents_chain(llm,prompt)
        retriever=retriever
        retrieval_chain=create_retrieval_chain(retriever,document_chain)

        # start=time.process_time()
        response=retrieval_chain.invoke({'input':user_prompt})
        # print(f"Response time :{time.process_time()-start}")

        st.write(response['answer'])



    # session_id=st.text_input("Session ID",value="default_session")
    # ## statefully manage chat history

    # if 'store' not in st.session_state:
    #     st.session_state.store={}
    #     doc = Document(page_content=combined_str, metadata={"source": "example", "author": "LangChain Docs"})
        
    #     # Step 2: Split the document into smaller chunks
    #     text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=30)
    #     docs = text_splitter.split_documents([doc])

    #     # Step 3: Use FAISS for chunk embeddings and retrieval
    #     embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")  # Embedding model for vectorization
    #     db = FAISS.from_documents(docs, embeddings)
    #     retriever = db.as_retriever()   

    #     contextualize_q_system_prompt=(
    #         "Given a chat history and the latest user question"
    #         "which might reference context in the chat history, "
    #         "formulate a standalone question which can be understood "
    #         "without the chat history. Do NOT answer the question, "
    #         "just reformulate it if needed and otherwise return it as is."
    #     )
    #     contextualize_q_prompt = ChatPromptTemplate.from_messages(
    #             [
    #                 ("system", contextualize_q_system_prompt),
    #                 MessagesPlaceholder("chat_history"),
    #                 ("human", "{input}"),
    #             ]
    #         )
        
    #     history_aware_retriever=create_history_aware_retriever(llm,retriever,contextualize_q_prompt)

    #     ## Answer question

    #     # Answer question
    #     system_prompt = (
    #             "You are an assistant for question-answering tasks. "
    #             "Use the following pieces of retrieved context to answer "
    #             "the question. If you don't know the answer, say that you "
    #             "don't know. Use three sentences maximum and keep the "
    #             "answer concise."
    #             "\n\n"
    #             "{context}"
    #         )
    #     qa_prompt = ChatPromptTemplate.from_messages(
    #             [
    #                 ("system", system_prompt),
    #                 MessagesPlaceholder("chat_history"),
    #                 ("human", "{input}"),
    #             ]
    #         )
        
    #     question_answer_chain=create_stuff_documents_chain(llm,qa_prompt)
    #     rag_chain=create_retrieval_chain(history_aware_retriever,question_answer_chain)

    #     def get_session_history(session:str)->BaseChatMessageHistory:
    #         if session_id not in st.session_state.store:
    #             st.session_state.store[session_id]=ChatMessageHistory()
    #         return st.session_state.store[session_id]
        
    #     conversational_rag_chain=RunnableWithMessageHistory(
    #         rag_chain,get_session_history,
    #         input_messages_key="input",
    #         history_messages_key="chat_history",
    #         output_messages_key="answer"
    #     )

    #     user_input = st.text_input("Your question:")
    #     if user_input:
    #         session_history=get_session_history(session_id)
    #         response = conversational_rag_chain.invoke(
    #             {"input": user_input},
    #             config={
    #                 "configurable": {"session_id":session_id}
    #             },  # constructs a key "abc123" in `store`.
    #         )
    #         st.write(st.session_state.store)
    #         st.write("Assistant:", response['answer'])
    #         st.write("Chat History:", session_history.messages)










