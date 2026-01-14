from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from huggingface_hub import InferenceClient
from typing import List, Tuple
import os
import random

class RAGService:
    def __init__(self):
        # Initialize Qdrant client (local Docker)
        self.client = QdrantClient(host="localhost", port=6333)
        
        # Initialize embedding model (HuggingFace - free)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embedding_dim = 384  # Dimension for all-MiniLM-L6-v2
        
        # Initialize HuggingFace LLM (FREE!)
        hf_token = os.getenv("HUGGINGFACE_API_KEY")
        self.llm = InferenceClient(token=hf_token)
        self.model_name = "mistralai/Mistral-7B-Instruct-v0.2"
        
        # Collection name prefix
        self.collection_prefix = "pdf_collection_"
    
    def _get_collection_name(self, session_id: str) -> str:
        """Get collection name for a session"""
        return f"{self.collection_prefix}{session_id}"
    
    def _create_collection(self, collection_name: str):
        """Create a new collection in Qdrant"""
        try:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_dim,
                    distance=Distance.COSINE
                )
            )
        except Exception as e:
            # Collection might already exist
            pass
    
    def store_document(self, session_id: str, chunks: List[str]) -> int:
        """Store document chunks in vector database"""
        collection_name = self._get_collection_name(session_id)
        
        # Create collection
        self._create_collection(collection_name)
        
        # Generate embeddings for all chunks
        embeddings = self.embedding_model.encode(chunks)
        
        # Create points for Qdrant
        points = [
            PointStruct(
                id=idx,
                vector=embedding.tolist(),
                payload={"text": chunk, "chunk_id": idx}
            )
            for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings))
        ]
        
        # Upload to Qdrant
        self.client.upsert(
            collection_name=collection_name,
            points=points
        )
        
        return len(chunks)
    
    def query(self, session_id: str, query: str, top_k: int = 3) -> Tuple[str, List[str]]:
        """Query the vector database and generate answer"""
        collection_name = self._get_collection_name(session_id)
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query)
        
        # Search in Qdrant
        search_results = self.client.search(
            collection_name=collection_name,
            query_vector=query_embedding.tolist(),
            limit=top_k
        )
        
        # Extract relevant chunks
        relevant_chunks = [hit.payload["text"] for hit in search_results]
        sources = [f"Chunk {hit.payload['chunk_id']}" for hit in search_results]
        
        # Create context from relevant chunks
        context = "\n\n".join(relevant_chunks)
        
        # Generate answer using LLM with chat completion
        messages = [
            {
                "role": "user",
                "content": f"""Based on the following context from the document, please answer the question.

Context:
{context}

Question: {query}

Answer:"""
            }
        ]
        
        try:
            response = self.llm.chat_completion(
                messages=messages,
                model=self.model_name,
                max_tokens=500,
                temperature=0.7
            )
            answer = response.choices[0].message.content
        except Exception as e:
            answer = f"Error generating answer: {str(e)}"
        
        return answer, sources
    
    def get_random_chunks(self, session_id: str, num_chunks: int) -> List[str]:
        """Get random chunks from the collection for MCQ generation"""
        collection_name = self._get_collection_name(session_id)
        
        try:
            # Use scroll to get all points
            scroll_result = self.client.scroll(
                collection_name=collection_name,
                limit=1000,  # Get up to 1000 chunks
                with_payload=True,
                with_vectors=False
            )
            
            points = scroll_result[0]  # First element is the list of points
            
            # Extract text from points
            all_chunks = [point.payload["text"] for point in points]
            
            # Return random selection
            num_to_fetch = min(num_chunks, len(all_chunks))
            if num_to_fetch == len(all_chunks):
                return all_chunks
            
            return random.sample(all_chunks, num_to_fetch)
            
        except Exception as e:
            print(f"Error getting random chunks: {str(e)}")
            # Fallback: try to retrieve by sequential IDs
            try:
                # Try to retrieve first N chunks
                points = self.client.retrieve(
                    collection_name=collection_name,
                    ids=list(range(num_chunks))
                )
                return [point.payload["text"] for point in points]
            except:
                return []
    
    def delete_session(self, session_id: str):
        """Delete a session's collection"""
        collection_name = self._get_collection_name(session_id)
        try:
            self.client.delete_collection(collection_name)
        except Exception as e:
            raise Exception(f"Error deleting session: {str(e)}")