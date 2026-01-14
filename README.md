# PDF Learning Hub

A full-stack web application that allows users to upload PDF documents, engage in conversational chat with the content using Retrieval-Augmented Generation (RAG), and generate multiple-choice questions (MCQs) for learning and assessment.

## Features

- **PDF Upload and Processing**: Upload PDF files and extract text content for analysis.
- **Conversational Chat**: Interact with your PDF content through an AI-powered chat interface using RAG technology.
- **MCQ Generation**: Automatically generate multiple-choice questions from the PDF content.
- **Quiz Mode**: Take quizzes with generated MCQs, submit answers, and receive instant feedback with scores and explanations.
- **Responsive UI**: Modern, responsive frontend built with Next.js and Tailwind CSS.

## Tech Stack

### Backend
- **FastAPI**: High-performance web framework for building APIs.
- **Python**: Core programming language.
- **PyPDF**: PDF text extraction.
- **Qdrant**: Vector database for document embeddings.
- **HuggingFace Mistral-7B-Instruct-v0.2**: Large language model for chat and MCQ generation.
- **LangChain**: Framework for building LLM applications.

### Frontend
- **Next.js**: React framework for server-side rendering and static site generation.
- **React**: JavaScript library for building user interfaces.
- **TypeScript**: Typed superset of JavaScript.
- **Tailwind CSS**: Utility-first CSS framework for styling.
- **Axios**: HTTP client for API requests.

### Infrastructure
- **Docker**: Containerization for easy deployment.
- **Docker Compose**: Orchestration of multi-container applications.

## Prerequisites

Before running this application, ensure you have the following installed:

- Python 3.8 or higher
- Node.js 18 or higher
- Docker and Docker Compose
- HuggingFace API key (set in `.env` file)

## Installation

### Option 1: Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd pdf-learning-hub
   ```

2. Create a `.env` file in the root directory with your HuggingFace API key:
   ```
   HUGGINGFACE_API_KEY=your_huggingface_api_key_here
   ```

3. Run the application using Docker Compose:
   ```bash
   docker-compose up --build
   ```

4. Access the application at `http://localhost:3000`

### Option 2: Local Development

#### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your OpenAI API key:
   ```
   HUGGINGFACE_API_KEY=your_huggingface_api_key_here
   ```

5. Start the backend server:
   ```bash
   python main.py
   ```
   The API will be available at `http://localhost:8000`

#### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```
   The frontend will be available at `http://localhost:3000`

## Usage

1. **Upload a PDF**: Click on the upload section and select a PDF file to process.
2. **Chat Mode**: After uploading, switch to chat mode to ask questions about the PDF content.
3. **MCQ Mode**: Generate multiple-choice questions from the PDF and take a quiz.
4. **New Session**: Start a new session to upload and work with different PDFs.

## API Endpoints

The backend provides the following REST API endpoints:

### Core Endpoints
- `GET /` - Health check endpoint
- `POST /upload` - Upload and process a PDF file
- `POST /chat` - Send a chat query and receive a response
- `POST /generate-mcq` - Generate MCQ questions from the PDF
- `POST /submit-mcq` - Submit MCQ answers and get results
- `DELETE /session/{session_id}` - Delete a session and its data

### Request/Response Examples

#### Upload PDF
```bash
curl -X POST "http://localhost:8000/upload" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@example.pdf"
```

#### Chat Query
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"session_id": "your-session-id", "query": "What is the main topic?"}'
```

#### Generate MCQs
```bash
curl -X POST "http://localhost:8000/generate-mcq" \
     -H "Content-Type: application/json" \
     -d '{"session_id": "your-session-id", "num_questions": 5}'
```

## Project Structure

```
pdf-learning-hub/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── requirements.txt        # Python dependencies
│   └── services/
│       ├── pdf_processor.py    # PDF text extraction
│       ├── rag_service.py      # RAG implementation
│       └── mcq_generator.py    # MCQ generation logic
├── frontend/
│   ├── app/
│   │   ├── page.tsx            # Main page component
│   │   ├── layout.tsx          # Layout component
│   │   └── components/         # React components
│   │       ├── UploadSection.tsx
│   │       ├── ChatSection.tsx
│   │       └── MCQSection.tsx
│   ├── package.json            # Node.js dependencies
│   └── tailwind.config.js      # Tailwind CSS configuration
├── docker/
│   └── docker-compose.yml      # Docker orchestration
└── README.md                   # This file
```
