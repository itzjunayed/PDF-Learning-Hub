"""
Simple test script to verify the backend API is working
Run this after starting the backend server
"""

import requests
import json

API_URL = "http://localhost:8000"

def test_health_check():
    """Test if the API is running"""
    print("Testing health check...")
    try:
        response = requests.get(f"{API_URL}/")
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_upload(pdf_path):
    """Test PDF upload"""
    print(f"\nTesting PDF upload: {pdf_path}")
    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': (pdf_path, f, 'application/pdf')}
            response = requests.post(f"{API_URL}/upload", files=files)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Upload successful!")
            print(f"✅ Session ID: {data['session_id']}")
            print(f"✅ Number of chunks: {data['num_chunks']}")
            return data['session_id']
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"❌ Error: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_chat(session_id, query):
    """Test chat functionality"""
    print(f"\nTesting chat with query: {query}")
    try:
        payload = {
            "session_id": session_id,
            "query": query
        }
        response = requests.post(f"{API_URL}/chat", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat successful!")
            print(f"✅ Answer: {data['answer'][:100]}...")
            print(f"✅ Sources: {data['sources']}")
            return True
        else:
            print(f"❌ Chat failed: {response.status_code}")
            print(f"❌ Error: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_mcq(session_id, num_questions=3):
    """Test MCQ generation"""
    print(f"\nTesting MCQ generation with {num_questions} questions")
    try:
        payload = {
            "session_id": session_id,
            "num_questions": num_questions
        }
        response = requests.post(f"{API_URL}/generate-mcq", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ MCQ generation successful!")
            print(f"✅ Generated {len(data['questions'])} questions")
            
            # Print first question as example
            if data['questions']:
                q = data['questions'][0]
                print(f"\nExample Question:")
                print(f"Q: {q['question']}")
                for i, opt in enumerate(q['options']):
                    marker = "✓" if opt['is_correct'] else " "
                    print(f"  {chr(65+i)}. {opt['text']} [{marker}]")
            return True
        else:
            print(f"❌ MCQ generation failed: {response.status_code}")
            print(f"❌ Error: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("PDF RAG API Test Script")
    print("=" * 60)
    
    # Test 1: Health check
    if not test_health_check():
        print("\n❌ API is not running. Please start the backend first.")
        exit(1)
    
    # Get PDF path from user
    pdf_path = input("\nEnter path to test PDF file (or press Enter to skip upload tests): ").strip()
    
    if pdf_path:
        # Test 2: Upload
        session_id = test_upload(pdf_path)
        
        if session_id:
            # Test 3: Chat
            test_chat(session_id, "What is this document about?")
            
            # Test 4: MCQ
            test_mcq(session_id, 2)
    
    print("\n" + "=" * 60)
    print("Testing complete!")
    print("=" * 60)
