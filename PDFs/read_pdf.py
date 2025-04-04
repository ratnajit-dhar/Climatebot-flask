from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceBgeEmbeddings, HuggingFaceInstructEmbeddings
from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.prompts import PromptTemplate
from langchain.docstore.document import Document
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_pdf_text(pdfs):
    text = ''
    for pdf in pdfs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(text):
    documents = [Document(page_content=text)]
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    text_chunk = text_splitter.split_documents(documents)
    return text_chunk

def get_embedding_model():
    return HuggingFaceBgeEmbeddings(model_name='sentence-transformers/all-miniLM-L6-v2')


def load_llm(huggingface_repo_id):
    llm = HuggingFaceEndpoint(
        repo_id=huggingface_repo_id,
        temperature = 0.5,
        model_kwargs={'token': "", 'max_length': '512'})
    
    return llm


# def get_vectorstore(text_chunks):

#     # openai_api_key = os.getenv('OPENAI_API_KEY')
#     # embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
#     embeddings = HuggingFaceInstructEmbeddings(model_name='hkunlp/instructor-xl')
#     vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
#     return vectorstore

# def save_vectorstore(vectorstore, path):
#     vectorstore.save(path)
#     print(f"Vectorstore saved to {path}")

# def load_vectorstore(path):
#     openai_api_key = os.getenv('OPENAI_API_KEY')
#     vectorstore = FAISS.load(path, OpenAIEmbeddings(openai_api_key=openai_api_key))
#     print(f"Vectorstore loaded from {path}")
#     return vectorstore

# Example usage
path = 'PDFs'
pdfs = [os.path.join(path, pdf) for pdf in os.listdir(path) if pdf.endswith('.pdf')]

documents = get_pdf_text(pdfs)
text_chunks = get_text_chunks(documents)
embedding = get_embedding_model()
db = FAISS.from_documents(text_chunks, embedding)
DB_FAISS_PATH = 'vectorstore.faiss'
db.save_local(DB_FAISS_PATH)
print('Check if the pdf is stored in the vectorstore')
# To load the vectorstore later from a local file
# loaded_vectorstore = load_vectorstore('vectorstore.faiss')