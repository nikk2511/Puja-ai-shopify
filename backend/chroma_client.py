"""
ChromaDB client wrapper for the Puja AI chatbot system.
Provides methods for initializing, adding documents, and querying the vector database.
"""

import os
import uuid
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import openai
from dotenv import load_dotenv

load_dotenv()

class ChromaClientWrapper:
    """Wrapper class for ChromaDB operations with OpenAI embeddings."""
    
    def __init__(self, collection_name: str = None, persist_dir: str = None):
        """
        Initialize ChromaDB client with OpenAI embeddings.
        
        Args:
            collection_name: Name of the ChromaDB collection
            persist_dir: Directory for persistent storage
        """
        self.collection_name = collection_name or os.getenv("CHROMA_COLLECTION_NAME", "puja_books")
        self.persist_dir = persist_dir or os.getenv("CHROMA_PERSIST_DIR", "./data/chroma")
        
        # Ensure persist directory exists
        os.makedirs(self.persist_dir, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        
        # Set up OpenAI embeddings
        api_key = os.getenv("OPENAI_API_KEY")
        self.embed_model = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
        
        # Initialize OpenAI embedding function
        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=api_key,
            model_name=self.embed_model
        )
        
        # Get or create collection
        self.collection = None
        self.init_chroma()
    
    def init_chroma(self):
        """Initialize or get existing ChromaDB collection."""
        try:
            # Try to get existing collection
            self.collection = self.client.get_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function
            )
            print(f"Connected to existing collection: {self.collection_name}")
        except Exception:
            # Create new collection if it doesn't exist
            self.collection = self.client.create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function
            )
            print(f"Created new collection: {self.collection_name}")
    
    def add_documents(self, docs: List[Dict[str, Any]]) -> bool:
        """
        Add documents to the ChromaDB collection.
        
        Args:
            docs: List of documents, each containing 'page_content' and 'metadata'
            
        Returns:
            bool: Success status
        """
        try:
            documents = []
            metadatas = []
            ids = []
            
            for doc in docs:
                page_content = doc.get('page_content', '')
                metadata = doc.get('metadata', {})
                
                # Generate unique ID if not provided
                doc_id = metadata.get('chunk_id', str(uuid.uuid4()))
                
                documents.append(page_content)
                metadatas.append(metadata)
                ids.append(doc_id)
            
            # Add to collection
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            print(f"Added {len(docs)} documents to collection")
            return True
            
        except Exception as e:
            print(f"Error adding documents: {e}")
            return False
    
    def query(self, query_text: str, k: int = 8) -> List[Dict[str, Any]]:
        """
        Query the ChromaDB collection for similar documents.
        
        Args:
            query_text: The query string
            k: Number of results to return
            
        Returns:
            List of documents with page_content, metadata, and distance
        """
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=k
            )
            
            # Format results
            formatted_results = []
            
            if results['documents'] and len(results['documents']) > 0:
                documents = results['documents'][0]
                metadatas = results['metadatas'][0] if results['metadatas'] else [{}] * len(documents)
                distances = results['distances'][0] if results['distances'] else [0.0] * len(documents)
                
                for doc, metadata, distance in zip(documents, metadatas, distances):
                    formatted_results.append({
                        'page_content': doc,
                        'metadata': metadata,
                        'distance': distance
                    })
            
            return formatted_results
            
        except Exception as e:
            print(f"Error querying collection: {e}")
            return []
    
    def get_doc_sources(self, documents: List[Dict[str, Any]]) -> List[str]:
        """
        Convert document metadata to human-readable source citations.
        
        Args:
            documents: List of documents with metadata
            
        Returns:
            List of formatted source strings
        """
        sources = []
        
        for doc in documents:
            metadata = doc.get('metadata', {})
            book_title = metadata.get('book_title', 'Unknown Book')
            page = metadata.get('page', 'Unknown')
            chunk_id = metadata.get('chunk_id', 'Unknown')
            
            source = f"Book: {book_title}, Page: {page}, Chunk: {chunk_id}"
            sources.append(source)
        
        return sources
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the collection.
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "document_count": count,
                "persist_dir": self.persist_dir
            }
        except Exception as e:
            print(f"Error getting collection info: {e}")
            return {
                "collection_name": self.collection_name,
                "document_count": 0,
                "persist_dir": self.persist_dir,
                "error": str(e)
            }
    
    def delete_collection(self) -> bool:
        """
        Delete the entire collection.
        
        Returns:
            bool: Success status
        """
        try:
            self.client.delete_collection(name=self.collection_name)
            print(f"Deleted collection: {self.collection_name}")
            return True
        except Exception as e:
            print(f"Error deleting collection: {e}")
            return False
    
    def check_if_document_exists(self, chunk_id: str) -> bool:
        """
        Check if a document with given chunk_id already exists.
        
        Args:
            chunk_id: The unique chunk identifier
            
        Returns:
            bool: True if document exists
        """
        try:
            result = self.collection.get(ids=[chunk_id])
            return len(result['ids']) > 0
        except Exception:
            return False

# Factory function for creating ChromaDB client
def create_chroma_client(collection_name: str = None, persist_dir: str = None) -> ChromaClientWrapper:
    """
    Factory function to create ChromaDB client wrapper.
    
    Args:
        collection_name: Name of the collection
        persist_dir: Persistence directory
        
    Returns:
        ChromaClientWrapper instance
    """
    return ChromaClientWrapper(collection_name, persist_dir)
