'use client'

import { useState } from 'react'
import axios from 'axios'

interface MCQOption {
  text: string
  is_correct: boolean
}

interface MCQQuestion {
  question: string
  options: MCQOption[]
  explanation: string
  correct_answer: string
}

interface MCQSectionProps {
  sessionId: string
  apiUrl: string
}

export default function MCQSection({ sessionId, apiUrl }: MCQSectionProps) {
  const [numQuestions, setNumQuestions] = useState(5)
  const [questions, setQuestions] = useState<MCQQuestion[]>([])
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [selectedAnswers, setSelectedAnswers] = useState<{ [key: number]: number }>({})
  const [showResults, setShowResults] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const generateQuestions = async () => {
    setIsLoading(true)
    setError(null)
    setQuestions([])
    setSelectedAnswers({})
    setShowResults(false)
    setCurrentQuestion(0)

    try {
      const response = await axios.post(`${apiUrl}/generate-mcq`, {
        session_id: sessionId,
        num_questions: numQuestions,
      })

      setQuestions(response.data.questions)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate questions')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSelectAnswer = (optionIndex: number) => {
    if (showResults) return

    setSelectedAnswers({
      ...selectedAnswers,
      [currentQuestion]: optionIndex,
    })
  }

  const handleNext = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1)
    }
  }

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1)
    }
  }

  const handleSubmit = () => {
    setShowResults(true)
    setCurrentQuestion(0)
  }

  const calculateScore = () => {
    let correct = 0
    questions.forEach((question, index) => {
      const selectedOption = selectedAnswers[index]
      if (selectedOption !== undefined && question.options[selectedOption].is_correct) {
        correct++
      }
    })
    return correct
  }

  const getOptionLabel = (index: number) => {
    return String.fromCharCode(65 + index) // A, B, C, D
  }

  if (questions.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-8">
        <div className="text-center mb-8">
          <div className="inline-block p-4 bg-green-100 rounded-full mb-4">
            <svg
              className="w-16 h-16 text-green-500"
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
          </div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">
            Generate MCQ Questions
          </h2>
          <p className="text-gray-600">
            Create multiple-choice questions from your PDF document
          </p>
        </div>

        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Number of Questions (1-15)
            </label>
            <input
              type="number"
              min="1"
              max="15"
              value={numQuestions}
              onChange={(e) => setNumQuestions(Math.min(15, Math.max(1, parseInt(e.target.value) || 1)))}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>

          <button
            onClick={generateQuestions}
            disabled={isLoading}
            className={`w-full py-3 rounded-lg font-semibold transition ${
              isLoading
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-green-500 text-white hover:bg-green-600'
            }`}
          >
            {isLoading ? 'Generating Questions...' : 'Generate Questions'}
          </button>

          {error && (
            <div className="p-4 bg-red-50 rounded-lg">
              <p className="text-red-700 text-center">{error}</p>
            </div>
          )}
        </div>
      </div>
    )
  }

  const currentQ = questions[currentQuestion]
  const selectedOption = selectedAnswers[currentQuestion]
  const score = showResults ? calculateScore() : 0

  return (
    <div className="bg-white rounded-lg shadow-lg p-8">
      {/* Header */}
      {showResults ? (
        <div className="mb-8 text-center">
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
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <h2 className="text-3xl font-bold text-gray-800 mb-2">
            Your Score: {score} / {questions.length}
          </h2>
          <p className="text-gray-600">
            {((score / questions.length) * 100).toFixed(0)}% Correct
          </p>
        </div>
      ) : (
        <div className="mb-6">
          <div className="flex justify-between items-center mb-2">
            <h2 className="text-xl font-bold text-gray-800">
              Question {currentQuestion + 1} of {questions.length}
            </h2>
            <button
              onClick={handleSubmit}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
            >
              Submit Test
            </button>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-green-500 h-2 rounded-full transition-all"
              style={{ width: `${((currentQuestion + 1) / questions.length) * 100}%` }}
            ></div>
          </div>
        </div>
      )}

      {/* Question */}
      <div className="mb-6">
        <h3 className="text-xl font-semibold text-gray-800 mb-4">
          {currentQ.question}
        </h3>

        {/* Options */}
        <div className="space-y-3">
          {currentQ.options.map((option, index) => {
            const isSelected = selectedOption === index
            const isCorrect = option.is_correct
            const showCorrectness = showResults

            let className = 'p-4 border-2 rounded-lg cursor-pointer transition '
            
            if (showCorrectness) {
              if (isCorrect) {
                className += 'border-green-500 bg-green-50 '
              } else if (isSelected && !isCorrect) {
                className += 'border-red-500 bg-red-50 '
              } else {
                className += 'border-gray-300 '
              }
            } else {
              className += isSelected
                ? 'border-blue-500 bg-blue-50 '
                : 'border-gray-300 hover:border-blue-300 '
            }

            return (
              <div
                key={index}
                onClick={() => handleSelectAnswer(index)}
                className={className}
              >
                <div className="flex items-center">
                  <span className="font-semibold mr-3 text-gray-700">
                    {getOptionLabel(index)}.
                  </span>
                  <span className="text-gray-800">{option.text}</span>
                  {showCorrectness && isCorrect && (
                    <span className="ml-auto text-green-500">✓</span>
                  )}
                  {showCorrectness && isSelected && !isCorrect && (
                    <span className="ml-auto text-red-500">✗</span>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Explanation */}
      {showResults && (
        <div className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <h4 className="font-semibold text-gray-800 mb-2">Explanation:</h4>
          <p className="text-gray-700">{currentQ.explanation}</p>
        </div>
      )}

      {/* Navigation */}
      <div className="flex justify-between">
        <button
          onClick={handlePrevious}
          disabled={currentQuestion === 0}
          className={`px-6 py-2 rounded-lg font-semibold transition ${
            currentQuestion === 0
              ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
              : 'bg-gray-300 text-gray-700 hover:bg-gray-400'
          }`}
        >
          Previous
        </button>

        {showResults && currentQuestion === questions.length - 1 ? (
          <button
            onClick={() => {
              setQuestions([])
              setShowResults(false)
              setSelectedAnswers({})
              setCurrentQuestion(0)
            }}
            className="px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition font-semibold"
          >
            Generate New Test
          </button>
        ) : (
          <button
            onClick={handleNext}
            disabled={currentQuestion === questions.length - 1}
            className={`px-6 py-2 rounded-lg font-semibold transition ${
              currentQuestion === questions.length - 1
                ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                : 'bg-blue-500 text-white hover:bg-blue-600'
            }`}
          >
            Next
          </button>
        )}
      </div>
    </div>
  )
}
