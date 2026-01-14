'use client'

import { useState } from 'react'
import axios from 'axios'

const API_URL = 'http://localhost:8000'

interface UploadSectionProps {
  onUploadComplete: (sessionId: string) => void
}

export default function UploadSection({ onUploadComplete }: UploadSectionProps) {
  const [file, setFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [progress, setProgress] = useState<string | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      if (selectedFile.type === 'application/pdf') {
        setFile(selectedFile)
        setError(null)
      } else {
        setError('Please select a PDF file')
        setFile(null)
      }
    }
  }

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first')
      return
    }

    setIsUploading(true)
    setError(null)
    setProgress('Uploading file...')

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await axios.post(`${API_URL}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      setProgress('Processing complete!')
      setTimeout(() => {
        onUploadComplete(response.data.session_id)
      }, 500)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload file')
      setProgress(null)
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-8">
      <div className="text-center mb-8">
        <div className="inline-block p-4 bg-blue-100 rounded-full mb-4">
          <svg
            className="w-16 h-16 text-blue-500"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            />
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-gray-800 mb-2">
          Upload Your PDF Document
        </h2>
        <p className="text-gray-600">
          Upload a PDF file to start chatting or generating MCQ questions
        </p>
      </div>

      <div className="space-y-6">
        {/* File Input */}
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition">
          <input
            type="file"
            accept=".pdf"
            onChange={handleFileChange}
            className="hidden"
            id="file-upload"
          />
          <label
            htmlFor="file-upload"
            className="cursor-pointer flex flex-col items-center"
          >
            <svg
              className="w-12 h-12 text-gray-400 mb-3"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            {file ? (
              <p className="text-blue-600 font-semibold">{file.name}</p>
            ) : (
              <p className="text-gray-600">
                Click to select a PDF file or drag and drop
              </p>
            )}
          </label>
        </div>

        {/* Upload Button */}
        <button
          onClick={handleUpload}
          disabled={!file || isUploading}
          className={`w-full py-3 rounded-lg font-semibold transition ${!file || isUploading
            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
            : 'bg-blue-500 text-white hover:bg-blue-600'
            }`}
        >
          {isUploading ? 'Processing...' : 'Upload and Process'}
        </button>

        {/* Progress */}
        {progress && (
          <div className="p-4 bg-blue-50 rounded-lg">
            <p className="text-blue-700 text-center">{progress}</p>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="p-4 bg-red-50 rounded-lg">
            <p className="text-red-700 text-center">{error}</p>
          </div>
        )}
      </div>
    </div>
  )
}
