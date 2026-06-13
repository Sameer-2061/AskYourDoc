import os
import fitz  
import docx
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer, util
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# 1. SETUP GEMINI (Initial config)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 2. SETUP FASTAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. SETUP MONGODB & EMBEDDINGS
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client['Final_AI_DB'] 
files_collection = db['files']
chats_collection = db['chats']
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def extract_text(file: UploadFile) -> str:
    ext = file.filename.lower().split('.')[-1]
    if ext == "txt":
        return file.file.read().decode("utf-8")
    elif ext == "pdf":
        doc = fitz.open(stream=file.file.read(), filetype="pdf")
        return "\n".join([page.get_text() for page in doc])
    elif ext == "docx":
        with open(f"temp_{file.filename}", "wb") as f:
            f.write(file.file.read())
        doc = docx.Document(f"temp_{file.filename}")
        os.remove(f"temp_{file.filename}")
        return "\n".join([para.text for para in doc.paragraphs])
    else:
        raise ValueError("Unsupported file format")

@app.post("/upload/")
async def upload_files(files: List[UploadFile] = File(...)):
    for file in files:
        text = extract_text(file)
        embedding = embedding_model.encode(text, convert_to_tensor=True)
        files_collection.insert_one({
            "filename": file.filename,
            "content": text,
            "embedding": embedding.tolist()
        })
    return {"message": "Files embedded and saved to MongoDB successfully!"}

class QuestionInput(BaseModel):
    chat_id: str
    question: str
    top_k: int = 1
    mode: str = "document" 

# Helper function to try multiple models (SDE Fallback Logic)
def get_gemini_response(prompt: str) -> str:
    # List of models from your terminal, ordered by preference
    models_to_try = [
        'gemini-2.5-flash',
        'gemini-2.0-flash',
        'gemini-2.0-flash-lite'
    ]
    
    last_error = None
    for model_name in models_to_try:
        try:
            llm_model = genai.GenerativeModel(model_name)
            response = llm_model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Model {model_name} failed. Trying next... Error: {e}")
            last_error = e
            continue
            
    # If all models fail, raise the last error
    raise Exception(f"All models failed. Last error: {last_error}")


@app.post("/ask/")
async def ask_question(data: QuestionInput):
    
    # --- GLOBAL MODE ---
    if data.mode == "global":
        prompt = f"""You are a highly intelligent and helpful AI assistant. 
        Answer the following question globally based on your general knowledge:
        Question: {data.question}"""
        
        final_answer = get_gemini_response(prompt)

    # --- DOCUMENT (RAG) MODE ---
    else:
        question_embedding = embedding_model.encode(data.question, convert_to_tensor=True)
        all_files = list(files_collection.find())

        if not all_files:
            return {"answer": "No documents found in database. Please upload a document first or switch to Global Mode."}

        scores = []
        for file in all_files:
            content_embedding = embedding_model.encode(file["content"], convert_to_tensor=True)
            score = util.pytorch_cos_sim(question_embedding, content_embedding).item()
            scores.append((file, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        top_files = scores[:data.top_k]

        answer_context = "\n\n".join([file["content"] for file, _ in top_files])
        
        prompt = f"""
        Read the following Document Context carefully:
        {answer_context}

        Now, answer this question based ONLY on the context above. If the answer is not in the context, say so:
        {data.question}
        """
        
        final_answer = get_gemini_response(prompt)

    # Save to MongoDB
    chats_collection.insert_one({
        "chat_id": data.chat_id,
        "question": data.question,
        "answer": final_answer,
        "mode": data.mode
    })

    return {"answer": final_answer}