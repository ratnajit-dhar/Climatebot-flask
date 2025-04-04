from flask import Flask, render_template, request, jsonify, send_file
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_huggingface import HuggingFaceEndpoint, HuggingFaceEmbeddings
from huggingface_hub import login
from dotenv import load_dotenv
import os
load_dotenv()
app = Flask(__name__)

# Initialize Hugging Face token
HUGGINGFACE_TOKEN = os.getenv('HUGGINGFACE_TOKEN')
login(token=HUGGINGFACE_TOKEN)

# Define the path to your saved vector store
DB_FAISS_PATH = 'vectorstore.faiss'

# Initialize global variables
qa_chain = None
messages = [
    {
        "role": "assistant",
        "content": "Hello! I am ClimateBot, here to answer your questions. I am designed to help answer any question you may have based on the provided documents you will find in the 'Documents' section."
    }
]

def load_vectorstore():
    embedding = HuggingFaceEmbeddings(model_name='sentence-transformers/all-miniLM-L6-v2')
    db = FAISS.load_local(DB_FAISS_PATH, embedding, allow_dangerous_deserialization=True)
    return db

def load_llm(huggingface_repo_id):
    llm = HuggingFaceEndpoint(
        repo_id=huggingface_repo_id,
        temperature=0.5,
        task="text-generation",
        model_kwargs={"token": "", "max_length": "512"}
    )
    return llm

def initialize_qa_chain():
    global qa_chain
    if qa_chain is None:
        try:
            print("Initializing QA Chain...")  # Debug print
            db = load_vectorstore()
            retriever = db.as_retriever()
            llm = load_llm("mistralai/Mistral-7B-Instruct-v0.3")
            qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
            print("QA Chain initialized successfully")  # Debug print
        except Exception as e:
            print(f"Error initializing QA Chain: {str(e)}")  # Debug print
            raise e
    return qa_chain

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/initialize_chat', methods=['POST'])
def initialize_chat():
    try:
        initialize_qa_chain()
        return jsonify({"status": "success"})
    except Exception as e:
        print(f"Error in initialize_chat: {str(e)}")  # Debug print
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/chat')
def chat():
    return render_template('chat.html', messages=messages)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/documents')
def documents():
    return render_template('documents.html')

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.get_json()
        question = data.get('question')
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400

        if qa_chain is None:
            initialize_qa_chain()

        print(f"Processing question: {question}")  # Debug print
        response = qa_chain.run(question)
        print(f"Generated response: {response}")  # Debug print

        if response is None or response == "":
            return jsonify({'error': 'No response generated'}), 500

        messages.append({"role": "user", "content": question})
        messages.append({"role": "assistant", "content": response})
        return jsonify({'response': response})
    
    except Exception as e:
        print(f"Error in ask route: {str(e)}")  # Debug print
        return jsonify({'error': str(e)}), 500

@app.route('/clear_chat', methods=['POST'])
def clear_chat():
    global messages
    messages = [
        {
            "role": "assistant",
            "content": "Hello! I am ClimateBot, here to answer your questions. I am designed to help answer any question you may have based on the provided documents you will find in the 'Documents' section."
        }
    ]
    return jsonify({"status": "success"})

@app.route('/download/<filename>')
def download_file(filename):
    try:
        return send_file(
            f"PDFs/{filename}",
            as_attachment=True
        )
    except Exception as e:
        print(f"Error downloading file: {str(e)}")  # Debug print
        return str(e), 404

@app.errorhandler(Exception)
def handle_error(e):
    print(f"Unhandled error: {str(e)}")  # Debug print
    return jsonify({"error": "An unexpected error occurred"}), 500

if __name__ == '__main__':
    app.run(debug=True)