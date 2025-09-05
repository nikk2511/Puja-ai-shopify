"""
Embeddings and query processing helper functions.
Handles query rewriting, expansion, and other text processing utilities.
"""

import os
from openai import OpenAI
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import tiktoken

load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI()

def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    """
    Count tokens in a text string for a given model.
    
    Args:
        text: Input text
        model: Model name for tokenization
        
    Returns:
        Number of tokens
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception:
        # Fallback: rough estimation
        return len(text.split()) * 1.3

def rewrite_query(raw_user_text: str) -> str:
    """
    Rewrite/expand vague queries into detailed prompts.
    
    Default rewrite rule: if query is short (< 8 tokens) or lacks required subrequests,
    expand to include specific requirements.
    
    Args:
        raw_user_text: Original user query
        
    Returns:
        Expanded/rewritten query
    """
    # Clean the input
    cleaned_text = raw_user_text.strip()
    
    # Count tokens (rough estimation)
    token_count = len(cleaned_text.split())
    
    # Check if query needs expansion
    needs_expansion = (
        token_count < 8 or
        not any(keyword in cleaned_text.lower() for keyword in [
            'step', 'procedure', 'how to', 'materials', 'timing', 'mantra'
        ])
    )
    
    if needs_expansion:
        # Apply default expansion template
        expanded_query = f"""Provide a step-by-step procedure for '{cleaned_text}'. Include:
1) A numbered step-by-step procedure
2) A bullet list of required materials with exact names
3) Any special timings or auspicious days
4) Mantras or short chants (if present in the sources)
5) Source citations (book name + page) for each major step or claim

Only use information from the indexed books."""
        
        return expanded_query
    
    return cleaned_text

def rewrite_query_with_llm(raw_user_text: str) -> str:
    """
    Use OpenAI to rewrite/clarify user queries for better retrieval.
    
    Args:
        raw_user_text: Original user query
        
    Returns:
        LLM-rewritten query
    """
    try:
        rewrite_prompt = f"""You are a query rewriter for a Hindu puja and ritual guidance system. 
Rewrite the following user query to be more specific and detailed for better document retrieval.

The rewritten query should:
1. Be clear and specific about what the user wants to know
2. Include relevant keywords for puja, rituals, materials, procedures
3. Maintain the original intent
4. Be optimized for semantic search in religious texts

Original query: "{raw_user_text}"

Rewritten query:"""

        response = openai_client.chat.completions.create(
            model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "user", "content": rewrite_prompt}
            ],
            temperature=0.0,
            max_tokens=200
        )
        
        rewritten = response.choices[0].message.content.strip()
        
        # Remove any quotes if the model added them
        if rewritten.startswith('"') and rewritten.endswith('"'):
            rewritten = rewritten[1:-1]
            
        return rewritten
        
    except Exception as e:
        print(f"Error in LLM query rewriting: {e}")
        # Fallback to rule-based rewriting
        return rewrite_query(raw_user_text)

def normalize_query(query: str) -> str:
    """
    Normalize query text for caching and comparison.
    
    Args:
        query: Input query
        
    Returns:
        Normalized query string
    """
    # Convert to lowercase, strip whitespace, normalize spaces
    normalized = ' '.join(query.lower().strip().split())
    return normalized

def extract_keywords(text: str) -> List[str]:
    """
    Extract relevant keywords from text for better search.
    
    Args:
        text: Input text
        
    Returns:
        List of extracted keywords
    """
    # Common puja-related keywords
    puja_keywords = [
        'puja', 'worship', 'ritual', 'ceremony', 'prayer', 'aarti', 'mantra',
        'offering', 'prasad', 'incense', 'flowers', 'lamp', 'diya', 'kalash',
        'idol', 'image', 'deity', 'god', 'goddess', 'temple', 'altar',
        'ganesh', 'durga', 'lakshmi', 'saraswati', 'shiva', 'vishnu', 'krishna',
        'hanuman', 'kali', 'ram', 'navratri', 'diwali', 'holi', 'janmashtami'
    ]
    
    words = text.lower().split()
    keywords = [word for word in words if word in puja_keywords]
    
    return list(set(keywords))  # Remove duplicates

def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate OpenAI embeddings for a list of texts.
    
    Args:
        texts: List of text strings
        
    Returns:
        List of embedding vectors
    """
    try:
        model = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
        
        response = openai.Embedding.create(
            model=model,
            input=texts
        )
        
        embeddings = [data['embedding'] for data in response['data']]
        return embeddings
        
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return []

def calculate_similarity_score(query_embedding: List[float], doc_embedding: List[float]) -> float:
    """
    Calculate cosine similarity between two embeddings.
    
    Args:
        query_embedding: Query embedding vector
        doc_embedding: Document embedding vector
        
    Returns:
        Similarity score (0-1)
    """
    try:
        import numpy as np
        
        # Convert to numpy arrays
        q = np.array(query_embedding)
        d = np.array(doc_embedding)
        
        # Calculate cosine similarity
        similarity = np.dot(q, d) / (np.linalg.norm(q) * np.linalg.norm(d))
        
        return float(similarity)
        
    except Exception as e:
        print(f"Error calculating similarity: {e}")
        return 0.0

def filter_relevant_chunks(chunks: List[Dict[str, Any]], min_similarity: float = 0.5) -> List[Dict[str, Any]]:
    """
    Filter chunks based on relevance/similarity threshold.
    
    Args:
        chunks: List of retrieved chunks with metadata
        min_similarity: Minimum similarity threshold
        
    Returns:
        Filtered list of relevant chunks
    """
    filtered_chunks = []
    
    for chunk in chunks:
        # Use distance from ChromaDB (lower is better)
        distance = chunk.get('distance', 1.0)
        similarity = 1.0 - distance  # Convert distance to similarity
        
        if similarity >= min_similarity:
            filtered_chunks.append(chunk)
    
    return filtered_chunks

def deduplicate_chunks(chunks: List[Dict[str, Any]], similarity_threshold: float = 0.9) -> List[Dict[str, Any]]:
    """
    Remove duplicate or very similar chunks.
    
    Args:
        chunks: List of chunks
        similarity_threshold: Threshold for considering chunks as duplicates
        
    Returns:
        Deduplicated list of chunks
    """
    if not chunks:
        return chunks
    
    deduplicated = [chunks[0]]  # Always keep the first (most relevant) chunk
    
    for chunk in chunks[1:]:
        is_duplicate = False
        chunk_content = chunk.get('page_content', '')
        
        for existing_chunk in deduplicated:
            existing_content = existing_chunk.get('page_content', '')
            
            # Simple text similarity check
            if len(chunk_content) > 0 and len(existing_content) > 0:
                overlap = len(set(chunk_content.split()) & set(existing_content.split()))
                union = len(set(chunk_content.split()) | set(existing_content.split()))
                
                if union > 0:
                    jaccard_similarity = overlap / union
                    if jaccard_similarity > similarity_threshold:
                        is_duplicate = True
                        break
        
        if not is_duplicate:
            deduplicated.append(chunk)
    
    return deduplicated

def estimate_cost(prompt_tokens: int, completion_tokens: int, model: str = "gpt-4o-mini") -> Dict[str, float]:
    """
    Estimate OpenAI API costs for a request.
    
    Args:
        prompt_tokens: Number of prompt tokens
        completion_tokens: Number of completion tokens
        model: Model name
        
    Returns:
        Dictionary with cost estimates
    """
    # Pricing as of late 2023 (update as needed)
    pricing = {
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},  # per 1k tokens
        "gpt-4o": {"input": 0.03, "output": 0.06},
        "gpt-3.5-turbo": {"input": 0.001, "output": 0.002},
        "text-embedding-3-small": {"input": 0.00002, "output": 0.0}
    }
    
    model_pricing = pricing.get(model, pricing["gpt-4o-mini"])
    
    input_cost = (prompt_tokens / 1000) * model_pricing["input"]
    output_cost = (completion_tokens / 1000) * model_pricing["output"]
    total_cost = input_cost + output_cost
    
    return {
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": total_cost,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens
    }
