"""
Main FastAPI application for the Puja AI Shopify chatbot.
Provides REST API endpoints for chat functionality, presets, and admin operations.
"""

import os
import json
import time
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

from openai import OpenAI
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import uvicorn
from dotenv import load_dotenv

from chroma_client import create_chroma_client
from embeddings_helper import (
    rewrite_query, rewrite_query_with_llm, normalize_query, 
    count_tokens, estimate_cost
)
from prompt_templates import (
    get_system_prompt, build_user_prompt, get_preset_questions
)
from ingestion import PDFIngestor

# Load environment variables
load_dotenv()

# OpenAI client will be initialized in startup event

# Initialize FastAPI app
app = FastAPI(
    title="Puja AI Shopify Chatbot",
    description="AI-powered Hindu puja and ritual guidance chatbot with RAG",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

# Global variables
chroma_client = None
product_mapping = {}
query_cache = {}  # Simple in-memory cache
rate_limit_store = {}  # Simple rate limiting
openai_client = None

# Pydantic models
class ChatRequest(BaseModel):
    question: str = Field(..., description="User's question or query")
    puja_id: Optional[str] = Field(None, description="Preset puja identifier")
    user_id: Optional[str] = Field(None, description="Optional user identifier")

class ChatResponse(BaseModel):
    ok: bool
    response: Optional[Dict[str, Any]] = None
    raw_llm_text: Optional[str] = None
    sources: Optional[List[Dict[str, Any]]] = None
    cost_estimate: Optional[Dict[str, float]] = None
    cache_hit: bool = False
    error: Optional[str] = None

class PresetResponse(BaseModel):
    presets: List[Dict[str, str]]

class HealthResponse(BaseModel):
    ok: bool
    status: str
    chroma_status: str
    openai_status: str
    timestamp: str

class UploadResponse(BaseModel):
    ok: bool
    message: str
    filename: Optional[str] = None
    chunks_created: Optional[int] = None

# Helper functions
def get_api_key_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """API key authentication for admin endpoints."""
    if not credentials:
        raise HTTPException(status_code=401, detail="API key required")
    
    expected_key = os.getenv("API_KEY")
    if not expected_key or credentials.credentials != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return credentials.credentials

def check_rate_limit(request: Request, max_requests: int = 60, window_minutes: int = 1):
    """Simple rate limiting by IP address."""
    client_ip = request.client.host
    current_time = datetime.now()
    
    # Clean old entries
    cutoff_time = current_time - timedelta(minutes=window_minutes)
    if client_ip in rate_limit_store:
        rate_limit_store[client_ip] = [
            req_time for req_time in rate_limit_store[client_ip] 
            if req_time > cutoff_time
        ]
    
    # Check current count
    if client_ip not in rate_limit_store:
        rate_limit_store[client_ip] = []
    
    if len(rate_limit_store[client_ip]) >= max_requests:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Add current request
    rate_limit_store[client_ip].append(current_time)

def load_product_mapping() -> Dict[str, str]:
    """Load product mapping from JSON file."""
    try:
        product_map_path = Path("./data/product_map.json")
        if product_map_path.exists():
            with open(product_map_path, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load product mapping: {e}")
    
    return {}

def find_product_matches(materials: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Find product matches for materials."""
    for material in materials:
        material_name = material.get("name", "").lower()
        
        # Try to find a match in product mapping
        product_match = None
        for product_key, product_url in product_mapping.items():
            if product_key.lower() in material_name or material_name in product_key.lower():
                product_match = product_url
                break
        
        material["product_match"] = product_match
    
    return materials

def generate_cache_key(question: str, puja_id: Optional[str] = None) -> str:
    """Generate cache key for query."""
    cache_input = f"{question}:{puja_id or ''}"
    return hashlib.md5(cache_input.encode()).hexdigest()

def parse_llm_response(raw_response: str) -> Dict[str, Any]:
    """Parse LLM response and extract JSON."""
    try:
        # Try to parse as direct JSON
        parsed = json.loads(raw_response.strip())
        return parsed
    except json.JSONDecodeError:
        # Try to extract JSON block
        import re
        json_match = re.search(r'```json\s*(\{.*\})\s*```', raw_response, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group(1))
                return parsed
            except json.JSONDecodeError:
                pass
        
        # Try to find JSON-like content
        json_match = re.search(r'(\{.*\})', raw_response, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group(1))
                return parsed
            except json.JSONDecodeError:
                pass
        
        # If all fails, return error structure
        return {
            "summary": "Error parsing response",
            "steps": [],
            "materials": [],
            "timings": [],
            "mantras": [],
            "sources": [],
            "notes": "Failed to parse LLM response as JSON"
        }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize global resources."""
    global chroma_client, product_mapping, openai_client
    
    print("Initializing Puja AI Chatbot...")
    
    # Initialize OpenAI client
    try:
        openai_client = OpenAI()
        print("OpenAI client initialized")
    except Exception as e:
        print(f"Warning: OpenAI client initialization failed: {e}")
    
    # Initialize ChromaDB client
    try:
        chroma_client = create_chroma_client()
        print("ChromaDB client initialized")
    except Exception as e:
        print(f"Warning: ChromaDB initialization failed: {e}")
    
    # Load product mapping
    product_mapping = load_product_mapping()
    print(f"Loaded {len(product_mapping)} product mappings")
    
    print("Startup complete!")

# API Endpoints

@app.post("/api/ask", response_model=ChatResponse)
async def ask_question(request: ChatRequest, http_request: Request):
    """
    Main chat endpoint - accepts questions and returns structured responses.
    """
    try:
        # Rate limiting
        check_rate_limit(http_request)
        
        # Determine the actual question to process
        if request.puja_id:
            # Use preset question
            preset_questions = get_preset_questions()
            if request.puja_id not in preset_questions:
                raise HTTPException(status_code=400, detail=f"Unknown puja_id: {request.puja_id}")
            
            expanded_question = preset_questions[request.puja_id]
        else:
            # Rewrite/expand user question
            expanded_question = rewrite_query(request.question)
        
        # Check cache
        cache_key = generate_cache_key(expanded_question, request.puja_id)
        if cache_key in query_cache:
            cached_response = query_cache[cache_key]
            cached_response["cache_hit"] = True
            return ChatResponse(**cached_response)
        
        # Query ChromaDB for relevant documents
        if not chroma_client:
            raise HTTPException(status_code=500, detail="ChromaDB not available")
        
        retrieved_docs = chroma_client.query(expanded_question, k=8)
        
        # Determine if we found relevant information in books
        use_fallback = not retrieved_docs or len(retrieved_docs) == 0
        
        if use_fallback:
            # No relevant books found - use OpenAI general knowledge as fallback
            system_prompt = """You are a knowledgeable Hindu puja and ritual expert assistant. Since no specific information was found in our sacred text database, please provide helpful guidance based on your general knowledge of Hindu traditions and practices.

Always structure your response as a JSON object with these fields:
- summary: Brief overview of the puja/ritual
- steps: Array of step objects with step_no, title, and instruction
- materials: Array of material objects with name, quantity, and description
- timings: Array of auspicious timing suggestions
- mantras: Array of relevant mantras or prayers
- notes: Important additional guidance or disclaimers

Remember to:
1. Provide authentic and respectful guidance
2. Suggest consulting local priests for specific regional customs
3. Include safety considerations where relevant
4. Be culturally sensitive and accurate"""

            user_prompt = f"""Please provide guidance for: {expanded_question}

Since this information is from general AI knowledge rather than specific sacred texts, please include a note about consulting authentic sources and local priests for complete guidance."""
            
            sources = [{
                "book": "AI General Knowledge",
                "page": "N/A", 
                "snippet": "Response generated using general AI knowledge of Hindu traditions",
                "distance": 0.0
            }]
        else:
            # Build prompt with retrieved documents as before
            system_prompt = get_system_prompt()
            user_prompt = build_user_prompt(expanded_question, retrieved_docs)
            
            # Prepare sources from retrieved documents
            sources = []
            for doc in retrieved_docs:
                metadata = doc.get("metadata", {})
                sources.append({
                    "book": metadata.get("book_title", "Unknown"),
                    "page": metadata.get("page", "Unknown"),
                    "snippet": doc.get("page_content", "")[:200] + "..." if len(doc.get("page_content", "")) > 200 else doc.get("page_content", ""),
                    "distance": doc.get("distance", 0.0)
                })
        
        # Count tokens for cost estimation
        prompt_tokens = count_tokens(system_prompt + user_prompt)
        
        # Call OpenAI
        chat_model = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
        max_tokens = int(os.getenv("MAX_TOKENS", "1500"))
        temperature = float(os.getenv("TEMPERATURE", "0.0"))
        
        response = openai_client.chat.completions.create(
            model=chat_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        raw_llm_text = response.choices[0].message.content
        completion_tokens = response.usage.completion_tokens
        
        # Parse LLM response
        parsed_response = parse_llm_response(raw_llm_text)
        
        # Add product matches to materials
        if "materials" in parsed_response and parsed_response["materials"]:
            parsed_response["materials"] = find_product_matches(parsed_response["materials"])
        
        # Calculate cost
        cost_estimate = estimate_cost(prompt_tokens, completion_tokens, chat_model)
        
        # Prepare response
        response_data = {
            "ok": True,
            "response": parsed_response,
            "raw_llm_text": raw_llm_text,
            "sources": sources,
            "cost_estimate": cost_estimate,
            "cache_hit": False
        }
        
        # Cache the response (with TTL of 24 hours)
        query_cache[cache_key] = response_data.copy()
        
        return ChatResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in ask_question: {e}")
        return ChatResponse(
            ok=False,
            error=f"Internal server error: {str(e)}"
        )

@app.get("/api/presets", response_model=PresetResponse)
async def get_presets():
    """Get list of preset puja buttons and questions."""
    try:
        preset_questions = get_preset_questions()
        
        presets = []
        for puja_id, question in preset_questions.items():
            # Create display name from puja_id
            display_name = puja_id.replace('_', ' ').title()
            
            presets.append({
                "id": puja_id,
                "name": display_name,
                "description": f"Get guidance for {display_name}",
                "question": question
            })
        
        return PresetResponse(presets=presets)
        
    except Exception as e:
        print(f"Error in get_presets: {e}")
        raise HTTPException(status_code=500, detail="Failed to load presets")

@app.post("/api/upload-pdf", response_model=UploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    api_key: str = Depends(get_api_key_auth)
):
    """Admin endpoint to upload and process PDF files."""
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Create pdfs directory if it doesn't exist
        pdfs_dir = Path("./pdfs")
        pdfs_dir.mkdir(exist_ok=True)
        
        # Save uploaded file
        file_path = pdfs_dir / file.filename
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process the PDF
        ingestor = PDFIngestor(pdf_dir="./pdfs", force=True)
        chunks_created = ingestor.process_single_pdf(file_path)
        
        if chunks_created > 0:
            return UploadResponse(
                ok=True,
                message=f"Successfully processed {file.filename}",
                filename=file.filename,
                chunks_created=chunks_created
            )
        else:
            return UploadResponse(
                ok=False,
                message=f"Failed to process {file.filename}",
                filename=file.filename,
                chunks_created=0
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in upload_pdf: {e}")
        return UploadResponse(
            ok=False,
            message=f"Error processing file: {str(e)}"
        )

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        # Check ChromaDB
        chroma_status = "ok"
        if chroma_client:
            try:
                collection_info = chroma_client.get_collection_info()
                if collection_info.get("error"):
                    chroma_status = f"error: {collection_info['error']}"
            except Exception as e:
                chroma_status = f"error: {str(e)}"
        else:
            chroma_status = "not initialized"
        
        # Check OpenAI
        openai_status = "ok" if os.getenv("OPENAI_API_KEY") else "no api key"
        
        # Check persist directory
        persist_dir = Path(os.getenv("CHROMA_PERSIST_DIR", "./data/chroma"))
        if not persist_dir.exists():
            chroma_status = "persist directory missing"
        
        overall_status = "healthy" if chroma_status == "ok" and openai_status == "ok" else "degraded"
        
        return HealthResponse(
            ok=True,
            status=overall_status,
            chroma_status=chroma_status,
            openai_status=openai_status,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        return HealthResponse(
            ok=False,
            status="error",
            chroma_status="unknown",
            openai_status="unknown",
            timestamp=datetime.now().isoformat()
        )

@app.get("/api/stats")
async def get_stats(api_key: str = Depends(get_api_key_auth)):
    """Admin endpoint to get system statistics."""
    try:
        stats = {
            "cache_entries": len(query_cache),
            "rate_limit_entries": len(rate_limit_store),
            "product_mappings": len(product_mapping)
        }
        
        if chroma_client:
            collection_info = chroma_client.get_collection_info()
            stats.update(collection_info)
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

@app.delete("/api/cache")
async def clear_cache(api_key: str = Depends(get_api_key_auth)):
    """Admin endpoint to clear query cache."""
    global query_cache
    cache_size = len(query_cache)
    query_cache.clear()
    
    return {
        "ok": True,
        "message": f"Cleared {cache_size} cache entries"
    }

@app.post("/api/reindex")
async def reindex_pdfs(api_key: str = Depends(get_api_key_auth)):
    """Admin endpoint to trigger full reindexing."""
    try:
        ingestor = PDFIngestor(pdf_dir="./pdfs", force=True)
        stats = ingestor.process_all_pdfs()
        
        return {
            "ok": True,
            "message": "Reindexing completed",
            "stats": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reindexing failed: {str(e)}")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Puja AI Shopify Chatbot",
        "version": "1.0.0",
        "description": "AI-powered Hindu puja and ritual guidance with RAG",
        "endpoints": {
            "chat": "/api/ask",
            "presets": "/api/presets",
            "health": "/api/health",
            "upload": "/api/upload-pdf",
            "docs": "/docs"
        }
    }

# Run the application
if __name__ == "__main__":
    host = os.getenv("FASTAPI_HOST", "0.0.0.0")
    port = int(os.getenv("FASTAPI_PORT", "8000"))
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=True
    )
