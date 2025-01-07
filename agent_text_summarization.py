import streamlit as st
import os
from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain import PromptTemplate
from langchain_groq import ChatGroq

def get_comments_summary(data):
    comments_str = data.get('comments', '')
    final_output = data.get('final_output', '')
    
    # Combine comments into a single string
    # comments_str = ' '.join(comments)
    
    # Combine comments string with final output
    combined_str = f"For this claim number my flow got these comments-{comments_str} and hence the final output is {final_output}"

    # Load model
    # load_dotenv(dotenv_path="C:/Users/abhishek221057/OneDrive - EXLService.com (I) Pvt. Ltd/Desktop/Agentic_bot/.env")
    api_key=st.secrets["GROQ_API_KEY"]
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable not set")
    llm=ChatGroq(groq_api_key=api_key,model="gemma2-9b-it")

    generictemplate="""
    Write a summary of the following comments which got generated because of the flow which was followed for the given claim number:
    Comments:{combined_str}
    """

    prompt=PromptTemplate(
        input_variables=['combined_str'],
        template=generictemplate
    )

    # complete_prompt=prompt.format(speech=combined_str)

    llm_chain=LLMChain(llm=llm,prompt=prompt)
    summary=llm_chain.run({'combined_str':combined_str})
    return summary
    # llm_chain = prompt | llm
    # try:
    #     summary = llm_chain.invoke({'combined_str': combined_str})
    # except Exception as e:
    #     raise RuntimeError(f"Error invoking LLM chain: {e}")

    # return summary
