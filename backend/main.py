from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
from dotenv import load_dotenv
import uvicorn
import tempfile

from services.pdf_processor import PDFProcessor
from services.rag_service import RAGService
from services.mcq_generator import MCQGenerator

load_dotenv()

app = FastAPI(title="PDF Learning Hub")

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

# Store MCQ sessions temporarily (in production, use Redis or database)
mcq_sessions: Dict[str, List[dict]] = {}

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

class MCQOptionPublic(BaseModel):
    text: str

class MCQQuestionPublic(BaseModel):
    question_id: int
    question: str
    options: List[MCQOptionPublic]

class MCQGenerateResponse(BaseModel):
    test_id: str
    questions: List[MCQQuestionPublic]

class MCQSubmitRequest(BaseModel):
    test_id: str
    answers: Dict[int, int]  # question_id -> option_index

class MCQOptionResult(BaseModel):
    text: str
    is_correct: bool

class MCQQuestionResult(BaseModel):
    question_id: int
    question: str
    options: List[MCQOptionResult]
    explanation: str
    correct_answer: str
    user_answer: Optional[int]
    is_correct: bool

class MCQSubmitResponse(BaseModel):
    score: int
    total: int
    percentage: float
    results: List[MCQQuestionResult]

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

@app.post("/generate-mcq", response_model=MCQGenerateResponse)
async def generate_mcq(request: MCQRequest):
    """Generate MCQ questions from the uploaded PDF (without answers)"""
    if request.num_questions < 1 or request.num_questions > 15:
        raise HTTPException(status_code=400, detail="Number of questions must be between 1 and 15")
    
    try:
        # Get relevant chunks from vector DB
        chunks = rag_service.get_random_chunks(request.session_id, request.num_questions * 2)
        
        # Generate MCQ questions (with answers)
        full_questions = mcq_generator.generate_questions(chunks, request.num_questions)
        
        # Generate unique test ID
        import uuid
        test_id = str(uuid.uuid4())
        
        # Store full questions with answers for later verification
        mcq_sessions[test_id] = full_questions
        
        # Return questions without correct answers
        public_questions = []
        for idx, q in enumerate(full_questions):
            public_questions.append({
                "question_id": idx,
                "question": q["question"],
                "options": [{"text": opt["text"]} for opt in q["options"]]
            })
        
        return MCQGenerateResponse(
            test_id=test_id,
            questions=public_questions
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating MCQ: {str(e)}")

@app.post("/submit-mcq", response_model=MCQSubmitResponse)
async def submit_mcq(request: MCQSubmitRequest):
    """Submit MCQ answers and get results with correct answers and explanations"""
    
    # Get stored questions
    if request.test_id not in mcq_sessions:
        raise HTTPException(status_code=404, detail="Test not found or expired")
    
    full_questions = mcq_sessions[request.test_id]
    
    # Calculate results
    results = []
    correct_count = 0
    
    for idx, question in enumerate(full_questions):
        user_answer = request.answers.get(idx)
        
        # Find correct answer index
        correct_index = None
        for opt_idx, opt in enumerate(question["options"]):
            if opt["is_correct"]:
                correct_index = opt_idx
                break
        
        is_correct = user_answer == correct_index
        if is_correct:
            correct_count += 1
        
        results.append({
            "question_id": idx,
            "question": question["question"],
            "options": question["options"],
            "explanation": question["explanation"],
            "correct_answer": question["correct_answer"],
            "user_answer": user_answer,
            "is_correct": is_correct
        })
    
    total = len(full_questions)
    percentage = (correct_count / total * 100) if total > 0 else 0
    
    # Clean up session after submission
    del mcq_sessions[request.test_id]
    
    return MCQSubmitResponse(
        score=correct_count,
        total=total,
        percentage=round(percentage, 2),
        results=results
    )

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