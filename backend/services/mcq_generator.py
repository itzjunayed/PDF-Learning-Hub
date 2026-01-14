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
        self.model_name = "mistralai/Mistral-7B-Instruct-v0.2"
    
    def _validate_and_fix_question(self, question: dict) -> dict:
        """Ensure only one option is marked as correct"""
        if not question.get("options") or len(question["options"]) == 0:
            return None
        
        # Count how many options are marked as correct
        correct_count = sum(1 for opt in question["options"] if opt.get("is_correct", False))
        
        if correct_count == 0:
            # No correct answer - mark first option as correct
            print(f"Warning: No correct answer found, marking first option as correct")
            question["options"][0]["is_correct"] = True
            for i in range(1, len(question["options"])):
                question["options"][i]["is_correct"] = False
            question["correct_answer"] = "A"
            
        elif correct_count > 1:
            # Multiple correct answers - keep only the first one
            print(f"Warning: Multiple correct answers found, keeping only the first one")
            first_correct_found = False
            correct_index = 0
            
            for i, opt in enumerate(question["options"]):
                if opt.get("is_correct", False) and not first_correct_found:
                    opt["is_correct"] = True
                    first_correct_found = True
                    correct_index = i
                else:
                    opt["is_correct"] = False
            
            # Update correct_answer letter
            question["correct_answer"] = chr(65 + correct_index)  # A, B, C, D
        
        # Verify exactly one correct answer
        correct_indices = [i for i, opt in enumerate(question["options"]) if opt.get("is_correct", False)]
        
        if len(correct_indices) != 1:
            print(f"Error: Still have {len(correct_indices)} correct answers after validation")
            return None
        
        # Ensure correct_answer matches the is_correct flag
        correct_index = correct_indices[0]
        question["correct_answer"] = chr(65 + correct_index)
        
        return question
    
    def generate_questions(self, chunks: List[str], num_questions: int) -> List[dict]:
        """Generate MCQ questions from document chunks"""
        questions = []
        
        # Combine chunks for context
        context = "\n\n".join(chunks[:num_questions * 2])[:3000]  # Limit context size
        
        prompt = f"""Based on the following text, generate {num_questions} multiple-choice questions (MCQ) with 4 options each.

IMPORTANT RULES:
- Each question must have EXACTLY ONE correct answer
- Mark is_correct as true for ONLY ONE option
- All other options must have is_correct as false

For each question:
1. Create a clear, specific question
2. Provide 4 options (A, B, C, D)
3. Mark ONLY ONE correct answer (is_correct: true)
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

Generate exactly {num_questions} questions in JSON format. Remember: ONLY ONE is_correct per question!"""
        
        messages = [{"role": "user", "content": prompt}]
        
        try:
            response = self.llm.chat_completion(
                messages=messages,
                model=self.model_name,
                max_tokens=2000,
                temperature=0.8
            )
            content = response.choices[0].message.content
            
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                questions_raw = json.loads(json_str)
            else:
                # Fallback: try to parse entire content as JSON
                questions_raw = json.loads(content)
            
            # Validate and fix each question
            for q in questions_raw[:num_questions]:
                validated_q = self._validate_and_fix_question(q)
                if validated_q:
                    questions.append(validated_q)
            
            # If we don't have enough valid questions, use fallback
            if len(questions) < num_questions:
                print(f"Only generated {len(questions)} valid questions, using fallback for remaining")
                remaining = num_questions - len(questions)
                fallback_questions = self._generate_fallback_questions(chunks, remaining)
                questions.extend(fallback_questions)
            
            return questions[:num_questions]
            
        except Exception as e:
            print(f"Error in main generation: {str(e)}")
            # Fallback: generate simple questions if JSON parsing fails
            return self._generate_fallback_questions(chunks, num_questions)
    
    def _generate_fallback_questions(self, chunks: List[str], num_questions: int) -> List[dict]:
        """Generate simple fallback questions if main generation fails"""
        questions = []
        
        for i in range(min(num_questions, len(chunks))):
            chunk = chunks[i][:600]  # Use first 600 chars
            
            prompt = f"""Based on this text, create ONE multiple choice question with 4 options.

CRITICAL: Mark EXACTLY ONE option as correct (is_correct: true). All others must be false.

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
}}

Remember: ONLY ONE is_correct should be true!"""
            
            messages = [{"role": "user", "content": prompt}]
            
            try:
                response = self.llm.chat_completion(
                    messages=messages,
                    model=self.model_name,
                    max_tokens=800,
                    temperature=0.8
                )
                content = response.choices[0].message.content
                
                # Try to extract JSON
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    q = json.loads(json_match.group())
                    validated_q = self._validate_and_fix_question(q)
                    if validated_q:
                        questions.append(validated_q)
            except Exception as e:
                print(f"Error generating question {i}: {str(e)}")
                # Create a basic fallback question
                questions.append(self._create_basic_question(chunk, i))
                continue
        
        return questions
    
    def _create_basic_question(self, chunk: str, index: int) -> dict:
        """Create a basic question as last resort fallback"""
        # Extract first sentence or first 100 characters
        first_sentence = chunk.split('.')[0][:100]
        
        return {
            "question": f"What does the document mention about: {first_sentence}?",
            "options": [
                {"text": "Information not provided in the text", "is_correct": False},
                {"text": f"It discusses: {first_sentence}", "is_correct": True},
                {"text": "This topic is not covered", "is_correct": False},
                {"text": "The document does not specify", "is_correct": False}
            ],
            "explanation": "This information is directly stated in the document text.",
            "correct_answer": "B"
        }