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
from langchain_huggingface import HuggingFaceEndpoint
import requests
from PIL import Image
from io import BytesIO


def generate_flowchart(data):
    comments_str = data.get('comments', '')
    final_output = data.get('final_output', '')
    
    # Combine comments into a single string
    # comments_str = ' '.join(comments)
    
    # Combine comments string with final output
    combined_str = f"This is complete flow-{comments_str} and hence the final output is {final_output}"
    # Load environment variables (e.g., Groq API keys)
    load_dotenv(dotenv_path="C:/Users/abhishek221057/OneDrive - EXLService.com (I) Pvt. Ltd/Desktop/Agentic_bot/.env")    
    api_key = os.getenv("HF_TOKEN")

    # if not api_key:
    #     raise ValueError("HF_TOKEN not found in environment variables")
    
    llm =  HuggingFaceEndpoint(repo_id="black-forest-labs/FLUX.1-dev",
                                    use_auth_token=api_key, height=1024,
                                    width=1024,
                                    guidance_scale=3.5,
                                    num_inference_steps=50,
                                    max_sequence_length=512,
                                    timeout = 300)
    
    text_prompt = f"Create a visually appealing flowchart based on this comments - {combined_str}"
    # with clear arrows, color-coded steps, and labeled checks. Each check should include the check number (e.g., Check 1) and a brief title (e.g., 'Eligibility Check'). Use green for successful checks, red for failed ones, and yellow for pending. The flowchart should start with Check 1 and branch to subsequent checks (e.g., Check 2, Check 3) based on conditions. Make the design clean, professional, and easy to follow, with smooth arrows, distinct colors, and readable text."
    # try:
    image_url = llm.invoke(text_prompt)  # This will return an image URL or image data
    print(f"Generated image URL: {image_url}")
    
    # Download the image if URL is returned
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))

    return img
    # except Exception as e:
    #     print(f"Error generating image: {e}")
    #     return None