from huggingface_hub import InferenceClient
from typing import List
import os
import json
import re

class MCQGenerator:
    def __init__(self):
        # Initialize HuggingFace LLM (FREE!)
        hf_token = os.getenv("HUGGINGFACE_API_KEY")
        self.llm = InferenceClient(token=hf_token)
        self.model_name = "mistralai/Mistral-7B-Instruct-v0.2"  # Free to use
    
    def generate_questions(self, chunks: List[str], num_questions: int) -> List[dict]:
        """Generate MCQ questions from document chunks"""
        questions = []
        
        # Combine chunks for context
        context = "\n\n".join(chunks[:num_questions])
        
        prompt = f"""Based on the following text, generate {num_questions} multiple-choice questions (MCQ) with 4 options each.

For each question:
1. Create a clear, specific question
2. Provide 4 options (A, B, C, D)
3. Mark the correct answer
4. Provide a brief explanation

Format your response as a JSON array with this structure:
[
  {{
    "question": "Question text here?",
    "options": [
      {{"text": "Option A", "is_correct": false}},
      {{"text": "Option B", "is_correct": true}},
      {{"text": "Option C", "is_correct": false}},
      {{"text": "Option D", "is_correct": false}}
    ],
    "explanation": "Explanation why B is correct",
    "correct_answer": "B"
  }}
]

Text:
{context}

Generate exactly {num_questions} questions in JSON format:"""
        
        try:
            response = self.llm.text_generation(
                prompt,
                model=self.model_name,
                max_new_tokens=2000,
                temperature=0.8,
                return_full_text=False
            )
            content = response
            
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                questions = json.loads(json_str)
            else:
                # Fallback: try to parse entire content as JSON
                questions = json.loads(content)
            
            # Ensure we have the right number of questions
            questions = questions[:num_questions]
            
            # Validate and format questions
            formatted_questions = []
            for q in questions:
                formatted_q = {
                    "question": q.get("question", ""),
                    "options": q.get("options", []),
                    "explanation": q.get("explanation", ""),
                    "correct_answer": q.get("correct_answer", "A")
                }
                formatted_questions.append(formatted_q)
            
            return formatted_questions
            
        except Exception as e:
            print(f"Error in main generation: {str(e)}")
            # Fallback: generate simple questions if JSON parsing fails
            return self._generate_fallback_questions(chunks, num_questions)
    
    def _generate_fallback_questions(self, chunks: List[str], num_questions: int) -> List[dict]:
        """Generate simple fallback questions if main generation fails"""
        questions = []
        
        for i in range(min(num_questions, len(chunks))):
            chunk = chunks[i][:500]  # Use first 500 chars
            
            prompt = f"""Based on this text, create ONE multiple choice question with 4 options.

Text: {chunk}

Respond with ONLY a JSON object in this exact format:
{{
  "question": "Your question?",
  "options": [
    {{"text": "Option A", "is_correct": false}},
    {{"text": "Option B", "is_correct": true}},
    {{"text": "Option C", "is_correct": false}},
    {{"text": "Option D", "is_correct": false}}
  ],
  "explanation": "Why the answer is correct",
  "correct_answer": "B"
}}"""
            
            try:
                response = self.llm.text_generation(
                    prompt,
                    model=self.model_name,
                    max_new_tokens=800,
                    temperature=0.8,
                    return_full_text=False
                )
                content = response
                
                # Try to extract JSON
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    q = json.loads(json_match.group())
                    questions.append(q)
            except Exception as e:
                print(f"Error generating question {i}: {str(e)}")
                # Skip if parsing fails
                continue
        
        return questions