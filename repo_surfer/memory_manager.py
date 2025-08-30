"""Memory management for conversation history and vector storage."""
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import chromadb
from chromadb.config import Settings
import json
import hashlib
import numpy as np
from datetime import datetime
import uuid

class MemoryManager:
    """Manages conversation memory using ChromaDB"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize the memory manager with ChromaDB"""
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        try:
            # Initialize Chroma client with the new API
            self.client = chromadb.PersistentClient(
                path=str(self.persist_directory)
            )
            
            # Simple embedding function that doesn't require downloads
            def simple_embedding(text: str) -> List[float]:
                # Create a simple hash-based embedding (not for production use)
                import hashlib
                import struct
                
                # Generate a deterministic hash from the text
                h = hashlib.sha256(text.encode()).digest()
                # Convert hash to list of floats between -1 and 1
                return [
                    (struct.unpack('!f', h[i*4:(i+1)*4])[0] / 2**31) % 2 - 1 
                    for i in range(384 // 4)  # 384-dimensional vector
                ]
            
            # Create or get collection with the new API
            self.collection = self.client.get_or_create_collection(
                name="conversation_memory",
                metadata={"hnsw:space": "cosine"},
                embedding_function=simple_embedding
            )
        except Exception as e:
            print(f"Error initializing ChromaDB: {e}")
            print("Falling back to in-memory storage...")
            # Fallback to in-memory client if persistent storage fails
            self.client = chromadb.Client()
            self.collection = self.client.create_collection(
                "conversation_memory",
                embedding_function=lambda x: [[0.0] * 384 for _ in x]  # Dummy embedding
            )
    
    def _generate_id(self, text: str) -> str:
        """Generate a deterministic ID for a text"""
        return hashlib.sha256(text.encode()).hexdigest()
    
    def add_conversation(
        self, 
        query: str, 
        response: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add a conversation to memory
        
        Args:
            query: User's query/message
            response: AI's response
            metadata: Additional metadata to store
            
        Returns:
            str: ID of the stored conversation
        """
        if metadata is None:
            metadata = {}
            
        # Add timestamp if not provided
        if 'timestamp' not in metadata:
            metadata['timestamp'] = datetime.utcnow().isoformat()
            
        # Generate a unique ID for this conversation
        conv_id = str(uuid.uuid4())
        
        try:
            # Store in ChromaDB
            self.collection.upsert(
                documents=[response],
                metadatas=[{'query': query, **metadata}],
                ids=[conv_id]
            )
            return conv_id
        except Exception as e:
            print(f"Error adding conversation to memory: {e}")
            # Fallback to simple file-based storage if Chroma fails
            try:
                memory_file = self.persist_directory / "fallback_memory.jsonl"
                with open(memory_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({
                        'id': conv_id,
                        'query': query,
                        'response': response,
                        'metadata': metadata
                    }) + '\n')
                return conv_id
            except Exception as fallback_error:
                print(f"Fallback storage also failed: {fallback_error}")
                return ""
    
    def search_memory(
        self, 
        query: str, 
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Search through conversation history"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=min(n_results, 10)  # Limit to 10 results max
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'id': results['ids'][0][i],
                    'document': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i]
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"Error searching memory: {e}")
            return []
    
    def get_conversation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent conversation history
        
        Args:
            limit: Maximum number of conversations to return
            
        Returns:
            List[Dict[str, Any]]: List of conversation items with id, query, response, and timestamp
        """
        try:
            # Get all items
            results = self.collection.get()
            if not results['ids']:
                return []
                
            # Sort by timestamp (newest first)
            items = sorted(
                zip(results['ids'], results['documents'], results['metadatas']),
                key=lambda x: x[2].get('timestamp', ''),
                reverse=True
            )
            
            # Format and limit results
            history = []
            for i, (doc_id, doc, meta) in enumerate(items):
                if i >= limit:
                    break
                history.append({
                    'id': doc_id,
                    'query': meta.get('query', ''),
                    'response': doc,
                    'timestamp': meta.get('timestamp', '')
                })
            
            return history
            
        except Exception as e:
            print(f"Error getting conversation history: {e}")
            return []
    
    def clear_memory(self) -> bool:
        """Clear all conversation memory"""
        try:
            self.collection.delete(where={})  # Delete all items
            return True
        except Exception as e:
            print(f"Error clearing memory: {e}")
            return False
    
    def save(self) -> bool:
        """Persist the memory to disk"""
        try:
            # Persistence is handled automatically in the new API
            # Just ensure the directory exists
            self.persist_directory.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error saving memory: {e}")
            return False
    
    def __del__(self):
        """Ensure data is saved when the object is destroyed"""
        self.save()
