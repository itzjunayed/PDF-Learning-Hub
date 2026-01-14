# PDF RAG Application

A full-stack application that allows users to upload PDF documents, chat with them using RAG (Retrieval Augmented Generation), and generate MCQ (Multiple Choice Questions) exams.

## Features

- 📄 **PDF Upload**: Upload and process PDF documents
- 💬 **Chat Mode**: Ask questions about your PDF using RAG
- 📝 **MCQ Mode**: Generate up to 15 multiple-choice questions from your PDF
- 🎯 **Instant Feedback**: See correct answers and explanations after completing MCQ
- 🔍 **Vector Search**: Uses Qdrant for efficient semantic search
- 🤖 **AI-Powered**: Leverages OpenAI GPT-3.5-turbo and HuggingFace embeddings

## Tech Stack

### Backend
- **FastAPI**: Web framework
- **LangChain**: RAG orchestration
- **Qdrant**: Vector database (local Docker)
- **OpenAI**: LLM (GPT-3.5-turbo)
- **HuggingFace**: Embeddings (all-MiniLM-L6-v2)

### Frontend
- **Next.js 14**: React framework
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **Axios**: API requests

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- Node.js 18 or higher
- Docker and Docker Compose
- Git

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd pdf-rag-app
```

### 2. Setup Qdrant (Vector Database)

Start Qdrant using Docker:

```bash
cd docker
docker-compose up -d
```

Verify Qdrant is running:
- Open browser to http://localhost:6333/dashboard
- You should see the Qdrant dashboard

### 3. Get OpenAI API Key

1. Go to https://platform.openai.com/
2. Sign up or log in
3. Navigate to API keys: https://platform.openai.com/api-keys
4. Click "Create new secret key"
5. Copy the key (you won't see it again!)

**Note**: OpenAI provides free trial credits for new accounts. After that, you'll need to add payment info, but GPT-3.5-turbo is very affordable (~$0.002 per 1K tokens).

### 4. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env and add your OpenAI API key
# Use nano, vim, or any text editor:
nano .env
```

In the `.env` file, replace `your_openai_api_key_here` with your actual OpenAI API key:

```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

### 5. Setup Frontend

Open a new terminal window:

```bash
cd frontend

# Install dependencies
npm install

# or if you prefer yarn:
yarn install
```

## Running the Application

### 1. Start Backend (Terminal 1)

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python main.py
```

The backend will start on http://localhost:8000

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Start Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

The frontend will start on http://localhost:3000

### 3. Access the Application

Open your browser and go to: http://localhost:3000

## How to Use

### Uploading a PDF

1. Click on the file upload area
2. Select a PDF file from your computer
3. Click "Upload and Process"
4. Wait for processing to complete (you'll receive a session ID)

### Chat Mode

1. After uploading, you'll be in Chat Mode by default
2. Type your question in the text area
3. Press Enter or click "Send"
4. The AI will respond based on your PDF content
5. Sources are shown below each answer

### MCQ Mode

1. Click the "📝 MCQ Mode" button
2. Select the number of questions (1-15)
3. Click "Generate Questions"
4. Wait for questions to generate
5. Answer each question by clicking an option
6. Navigate using Previous/Next buttons
7. Click "Submit Test" when ready
8. View your score, correct answers, and explanations

## Free Tier Limits

### OpenAI (GPT-3.5-turbo)
- **Free Trial**: $5 credit for new accounts (expires after 3 months)
- **Cost**: ~$0.002 per 1K tokens
- **Estimate**: ~1000-2000 questions with $5 credit
- **After free tier**: Very affordable, typically $0.50-$2.00 per month for moderate use

### HuggingFace Embeddings
- **Completely Free**: Runs locally
- **Model**: all-MiniLM-L6-v2
- **No API key needed**

### Qdrant
- **Completely Free**: Running in local Docker
- **No limits**: Runs on your machine

## Project Structure

```
pdf-rag-app/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── services/
│   │   ├── pdf_processor.py    # PDF extraction and chunking
│   │   ├── rag_service.py      # RAG and vector DB operations
│   │   └── mcq_generator.py    # MCQ question generation
│   ├── requirements.txt        # Python dependencies
│   └── .env                    # Environment variables
├── frontend/
│   ├── app/
│   │   ├── page.tsx           # Main page
│   │   ├── layout.tsx         # Root layout
│   │   ├── globals.css        # Global styles
│   │   └── components/
│   │       ├── UploadSection.tsx
│   │       ├── ChatSection.tsx
│   │       └── MCQSection.tsx
│   ├── package.json
│   └── next.config.js
└── docker/
    └── docker-compose.yml     # Qdrant setup
```

## API Endpoints

### POST /upload
Upload and process a PDF file

**Request**: multipart/form-data with PDF file

**Response**:
```json
{
  "session_id": "uuid",
  "message": "PDF uploaded and processed successfully",
  "num_chunks": 42
}
```

### POST /chat
Chat with the uploaded PDF

**Request**:
```json
{
  "session_id": "uuid",
  "query": "What is the main topic?"
}
```

**Response**:
```json
{
  "answer": "The main topic is...",
  "sources": ["Chunk 1", "Chunk 5"]
}
```

### POST /generate-mcq
Generate MCQ questions

**Request**:
```json
{
  "session_id": "uuid",
  "num_questions": 5
}
```

**Response**:
```json
{
  "questions": [
    {
      "question": "What is...?",
      "options": [
        {"text": "Option A", "is_correct": false},
        {"text": "Option B", "is_correct": true},
        {"text": "Option C", "is_correct": false},
        {"text": "Option D", "is_correct": false}
      ],
      "explanation": "B is correct because...",
      "correct_answer": "B"
    }
  ]
}
```

### DELETE /session/{session_id}
Delete a session and its data

## Troubleshooting

### Backend won't start
- Check if Python virtual environment is activated
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check if OpenAI API key is set in .env
- Verify Qdrant is running: http://localhost:6333/dashboard

### Frontend won't start
- Delete `node_modules` and `.next` folders
- Run `npm install` again
- Check if port 3000 is available

### Qdrant connection error
- Check if Docker is running: `docker ps`
- Restart Qdrant: `docker-compose restart`
- Check Qdrant logs: `docker-compose logs qdrant`

### OpenAI API errors
- Verify API key is correct in .env
- Check if you have credits: https://platform.openai.com/usage
- Ensure key has proper permissions

### PDF upload fails
- Check file size (keep under 10MB for free tier)
- Verify it's a valid PDF file
- Check backend logs for errors

## Development Tips

### Backend Development
- Use `uvicorn main:app --reload` for auto-reload during development
- Check logs in the terminal for debugging
- Test API endpoints using http://localhost:8000/docs (Swagger UI)

### Frontend Development
- Next.js has hot-reload enabled by default
- Check browser console for errors
- Use React DevTools for component debugging

## Stopping the Application

1. Stop frontend: Press `Ctrl+C` in the frontend terminal
2. Stop backend: Press `Ctrl+C` in the backend terminal
3. Stop Qdrant: `cd docker && docker-compose down`

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License

## Support

For questions or issues:
1. Check the Troubleshooting section
2. Review API documentation at http://localhost:8000/docs
3. Check Qdrant dashboard at http://localhost:6333/dashboard

## Acknowledgments

- OpenAI for GPT-3.5-turbo
- HuggingFace for free embeddings
- Qdrant for vector database
- LangChain for RAG framework
