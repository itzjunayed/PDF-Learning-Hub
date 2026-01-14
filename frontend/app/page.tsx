'use client'

import { useState } from 'react'
import axios from 'axios'
import UploadSection from './components/UploadSection'
import ChatSection from './components/ChatSection'
import MCQSection from './components/MCQSection'

const API_URL = 'http://localhost:8000'

export default function Home() {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [mode, setMode] = useState<'upload' | 'chat' | 'mcq'>('upload')
  const [isLoading, setIsLoading] = useState(false)

  const handleUploadComplete = (newSessionId: string) => {
    setSessionId(newSessionId)
    setMode('chat')
  }

  const resetSession = () => {
    if (sessionId) {
      axios.delete(`${API_URL}/session/${sessionId}`).catch(console.error)
    }
    setSessionId(null)
    setMode('upload')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            PDF RAG Application
          </h1>
          <p className="text-gray-600">
            Upload your PDF, chat with it, or generate MCQ questions
          </p>
        </div>

        {/* Main Content */}
        <div className="max-w-6xl mx-auto">
          {sessionId && (
            <div className="mb-6 bg-white rounded-lg shadow-md p-4">
              <div className="flex justify-between items-center">
                <div>
                  <p className="text-sm text-gray-600">Session ID:</p>
                  <p className="font-mono text-sm text-gray-800">{sessionId}</p>
                </div>
                <button
                  onClick={resetSession}
                  className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition"
                >
                  New Session
                </button>
              </div>
            </div>
          )}

          {/* Mode Selection */}
          {sessionId && (
            <div className="mb-6 bg-white rounded-lg shadow-md p-4">
              <div className="flex gap-4">
                <button
                  onClick={() => setMode('chat')}
                  className={`flex-1 py-3 rounded-lg font-semibold transition ${
                    mode === 'chat'
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  💬 Chat Mode
                </button>
                <button
                  onClick={() => setMode('mcq')}
                  className={`flex-1 py-3 rounded-lg font-semibold transition ${
                    mode === 'mcq'
                      ? 'bg-green-500 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  📝 MCQ Mode
                </button>
              </div>
            </div>
          )}

          {/* Content Sections */}
          {mode === 'upload' && (
            <UploadSection onUploadComplete={handleUploadComplete} />
          )}

          {mode === 'chat' && sessionId && (
            <ChatSection sessionId={sessionId} apiUrl={API_URL} />
          )}

          {mode === 'mcq' && sessionId && (
            <MCQSection sessionId={sessionId} apiUrl={API_URL} />
          )}
        </div>
      </div>
    </div>
  )
}
