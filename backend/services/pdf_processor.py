import uuid
from pypdf import PdfReader
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter

class PDFProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
    
    def generate_session_id(self) -> str:
        """Generate a unique session ID"""
        return str(uuid.uuid4())
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[str]:
        """Extract text from PDF and split into chunks"""
        try:
            reader = PdfReader(pdf_path)
            text = ""
            
            # Extract text from all pages
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            # Split text into chunks
            chunks = self.text_splitter.split_text(text)
            
            return chunks
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
