from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import tempfile
from dotenv import load_dotenv
import uvicorn

from services.pdf_processor import PDFProcessor
from services.rag_service import RAGService
from services.mcq_generator import MCQGenerator

load_dotenv()

app = FastAPI(title="PDF RAG Application")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
pdf_processor = PDFProcessor()
rag_service = RAGService()
mcq_generator = MCQGenerator()

# Pydantic models
class ChatRequest(BaseModel):
    session_id: str
    query: str
    
class ChatResponse(BaseModel):
    answer: str
    sources: List[str]

class MCQRequest(BaseModel):
    session_id: str
    num_questions: int

class MCQOption(BaseModel):
    text: str
    is_correct: bool

class MCQQuestion(BaseModel):
    question: str
    options: List[MCQOption]
    explanation: str
    correct_answer: str

class MCQResponse(BaseModel):
    questions: List[MCQQuestion]

class UploadResponse(BaseModel):
    session_id: str
    message: str
    num_chunks: int

@app.get("/")
async def root():
    return {"message": "PDF RAG API is running"}

@app.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """Upload a PDF file and process it"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    temp_path = None
    try:
        # Save uploaded file temporarily using tempfile
        content = await file.read()
        
        # Create a temporary file with .pdf extension
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_path = temp_file.name
            temp_file.write(content)
        
        # Process PDF
        session_id = pdf_processor.generate_session_id()
        chunks = pdf_processor.extract_text_from_pdf(temp_path)
        
        # Store in vector database
        num_chunks = rag_service.store_document(session_id, chunks)
        
        return UploadResponse(
            session_id=session_id,
            message=f"PDF uploaded and processed successfully",
            num_chunks=num_chunks
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")
    finally:
        # Clean up temp file
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with the uploaded PDF"""
    try:
        answer, sources = rag_service.query(request.session_id, request.query)
        return ChatResponse(answer=answer, sources=sources)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in chat: {str(e)}")

@app.post("/generate-mcq", response_model=MCQResponse)
async def generate_mcq(request: MCQRequest):
    """Generate MCQ questions from the uploaded PDF"""
    if request.num_questions < 1 or request.num_questions > 15:
        raise HTTPException(status_code=400, detail="Number of questions must be between 1 and 15")
    
    try:
        # Get relevant chunks from vector DB
        chunks = rag_service.get_random_chunks(request.session_id, request.num_questions * 2)
        
        # Generate MCQ questions
        questions = mcq_generator.generate_questions(chunks, request.num_questions)
        
        return MCQResponse(questions=questions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating MCQ: {str(e)}")

@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and its data"""
    try:
        rag_service.delete_session(session_id)
        return {"message": "Session deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)