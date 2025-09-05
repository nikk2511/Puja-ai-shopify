# Puja AI Shopify Backend

FastAPI backend for the Puja AI Shopify Chatbot with ChromaDB vector storage and OpenAI integration for Retrieval-Augmented Generation (RAG).

## Features

- **FastAPI** REST API with automatic documentation
- **ChromaDB** vector database for PDF content storage
- **OpenAI** embeddings (text-embedding-3-small) and chat completion
- **PDF Ingestion** pipeline with text extraction and chunking
- **RAG Implementation** with semantic search and context injection
- **Product Mapping** for Shopify integration
- **Caching** for improved performance
- **Rate Limiting** and security features
- **Docker** support for easy deployment

## Quick Start

### Local Development

1. **Install Python 3.10+:**
   ```bash
   python --version  # Should be 3.10+
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment:**
   ```bash
   cp env_example.txt .env
   # Edit .env with your API keys
   ```

5. **Prepare PDFs:**
   ```bash
   mkdir pdfs
   # Place your PDF files in the pdfs directory
   ```

6. **Run ingestion:**
   ```bash
   python ingestion.py --pdf_dir=./pdfs
   ```

7. **Start server:**
   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

8. **Visit API docs:**
   ```
   http://localhost:8000/docs
   ```

### Docker Setup

1. **Build and run:**
   ```bash
   docker build -t puja-ai-backend .
   docker run -p 8000:8000 --env-file .env puja-ai-backend
   ```

2. **Using docker-compose:**
   ```bash
   cd ../infra
   docker-compose up -d
   ```

## Environment Configuration

### Required Variables

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_EMBED_MODEL=text-embedding-3-small
OPENAI_CHAT_MODEL=gpt-4o-mini

# ChromaDB Configuration
CHROMA_PERSIST_DIR=./data/chroma
CHROMA_COLLECTION_NAME=puja_books

# FastAPI Configuration
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000

# Security
API_KEY=your_admin_api_key_here
```

### Optional Variables

```bash
# Cache Configuration
CACHE_HOST=localhost

# Shopify Integration
SHOPIFY_API_KEY=your_shopify_api_key
SHOPIFY_API_SECRET=your_shopify_api_secret
SHOPIFY_APP_URL=https://your-app-url.example.com

# Performance Tuning
MAX_TOKENS=1500
TEMPERATURE=0.0
```

## API Endpoints

### Public Endpoints

#### `POST /api/ask`
Main chat endpoint for asking questions.

**Request:**
```json
{
  "question": "How to perform Ganesh Puja?",
  "puja_id": "ganesh",  // optional preset ID
  "user_id": "user123"  // optional user identifier
}
```

**Response:**
```json
{
  "ok": true,
  "response": {
    "summary": "Ganesh Puja for home ceremony",
    "steps": [
      {
        "step_no": 1,
        "title": "Preparation",
        "instruction": "Clean the area and place Ganesh idol"
      }
    ],
    "materials": [
      {
        "name": "incense",
        "quantity": "1 pack",
        "product_match": "/products/incense-sticks"
      }
    ],
    "timings": ["Morning", "Before noon"],
    "mantras": ["Om Ganapataye Namah"],
    "sources": [
      {
        "book": "Ganesh Puja Guide",
        "page": 12,
        "snippet": "Place the idol facing east..."
      }
    ],
    "notes": "Consult local priest for specific timings"
  },
  "cache_hit": false,
  "cost_estimate": {
    "total_cost": 0.001234
  }
}
```

#### `GET /api/presets`
Get available preset puja types.

**Response:**
```json
{
  "presets": [
    {
      "id": "ganesh",
      "name": "Ganesh Puja",
      "description": "Lord Ganesha worship guidance"
    }
  ]
}
```

#### `GET /api/health`
Health check endpoint.

**Response:**
```json
{
  "ok": true,
  "status": "healthy",
  "chroma_status": "ok",
  "openai_status": "ok",
  "timestamp": "2023-12-01T10:00:00Z"
}
```

### Admin Endpoints

#### `POST /api/upload-pdf`
Upload and process PDF files (requires API key).

**Headers:**
```
Authorization: Bearer your_api_key_here
```

**Body:** Multipart form with PDF file

#### `GET /api/stats`
Get system statistics (requires API key).

#### `DELETE /api/cache`
Clear query cache (requires API key).

#### `POST /api/reindex`
Trigger full reindexing (requires API key).

## PDF Ingestion

### Ingestion Pipeline

The ingestion pipeline processes PDF files through several stages:

1. **Text Extraction** - Uses pdfplumber (fallback to PyPDF2)
2. **Text Cleaning** - Removes headers, footers, page numbers
3. **Chunking** - Splits into 1000-character chunks with 200-character overlap
4. **Embedding** - Generates OpenAI embeddings
5. **Storage** - Stores in ChromaDB with metadata

### Running Ingestion

```bash
# Basic ingestion
python ingestion.py --pdf_dir=./pdfs

# Force re-indexing
python ingestion.py --pdf_dir=./pdfs --force

# Process specific directory
python ingestion.py --pdf_dir=/path/to/pdfs
```

### Supported PDF Types

- Text-based PDFs (preferred)
- Scanned PDFs with OCR text layer
- Mixed content PDFs

### PDF Preparation Tips

1. **Quality:** Use high-quality, text-searchable PDFs
2. **Organization:** Name files descriptively (e.g., "Ganesh_Puja_Guide.pdf")
3. **Content:** Ensure PDFs contain relevant puja/ritual information
4. **Size:** Larger PDFs are automatically chunked for optimal retrieval

## ChromaDB Configuration

### Collection Setup

The system automatically creates and manages ChromaDB collections:

```python
# Collection configuration
COLLECTION_NAME = "puja_books"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
EMBEDDING_MODEL = "text-embedding-3-small"
```

### Data Structure

Each document chunk is stored with metadata:

```json
{
  "page_content": "Text content of the chunk",
  "metadata": {
    "book_title": "Ganesh Puja Guide",
    "page": 15,
    "chunk_id": "uuid-string",
    "chunk_index": 0,
    "source_file": "ganesh_puja_guide.pdf",
    "extraction_method": "pdfplumber"
  }
}
```

### Backup and Recovery

```bash
# Backup ChromaDB data
tar -czf chroma_backup.tar.gz data/chroma/

# Restore ChromaDB data
tar -xzf chroma_backup.tar.gz
```

## Retrieval-Augmented Generation (RAG)

### How RAG Works

1. **Query Processing** - User question is expanded/rewritten
2. **Semantic Search** - ChromaDB finds relevant text chunks
3. **Context Building** - Retrieved chunks are formatted for LLM
4. **LLM Generation** - OpenAI generates structured response
5. **Post-processing** - Product matching and source attribution

### Query Rewriting

The system automatically expands vague queries:

```python
# Input: "Ganesh puja"
# Expanded: "Provide step-by-step procedure for Ganesh Puja. Include..."
```

### Retrieval Parameters

```python
# Default retrieval settings
TOP_K = 8           # Number of chunks to retrieve
FETCH_K = 16        # Number of candidates to consider
MIN_SIMILARITY = 0.5  # Minimum similarity threshold
```

## Product Mapping

### Configuration

Product mapping connects materials to Shopify products:

```json
{
  "incense": "/products/dhoop-agarbatti",
  "red flowers": "/collections/flowers",
  "diya": "/products/oil-lamps-diya"
}
```

### Adding Products

1. **Edit mapping file:**
   ```bash
   vim data/product_map.json
   ```

2. **Restart server** to reload mappings

3. **Test mapping:**
   ```bash
   curl -X POST localhost:8000/api/ask \
        -H "Content-Type: application/json" \
        -d '{"question": "What materials needed for puja?"}'
   ```

## Security

### API Key Authentication

Admin endpoints require API key authentication:

```bash
# Set in environment
API_KEY=your_secure_api_key_here

# Use in requests
curl -H "Authorization: Bearer your_secure_api_key_here" \
     localhost:8000/api/upload-pdf
```

### Rate Limiting

Built-in rate limiting protects against abuse:

- **60 requests per minute** per IP address
- **Sliding window** implementation
- **Configurable limits** via environment variables

### CORS Configuration

Configure CORS for your domains:

```python
# In app.py
allow_origins=["https://your-domain.com", "https://shop.myshopify.com"]
```

## Performance Optimization

### Caching

The system implements multiple caching layers:

1. **Query Cache** - Caches responses for identical questions
2. **Embedding Cache** - Reuses embeddings for similar queries
3. **Redis Cache** - Optional external cache for production

### Monitoring

```bash
# Check API performance
curl localhost:8000/api/stats

# Monitor ChromaDB
du -sh data/chroma/

# Check OpenAI usage
# Monitor via OpenAI dashboard
```

### Scaling Tips

1. **Horizontal Scaling** - Run multiple instances behind load balancer
2. **Database Scaling** - Consider Pinecone for larger datasets
3. **Caching** - Use Redis for production deployments
4. **CDN** - Cache static responses via CDN

## Troubleshooting

### Common Issues

1. **ChromaDB Errors:**
   ```bash
   # Fix permissions
   chmod -R 755 data/chroma/
   
   # Reset database
   rm -rf data/chroma/
   python ingestion.py --pdf_dir=./pdfs --force
   ```

2. **OpenAI API Errors:**
   ```bash
   # Check API key
   curl https://api.openai.com/v1/models \
        -H "Authorization: Bearer $OPENAI_API_KEY"
   
   # Check usage limits
   # Visit OpenAI dashboard
   ```

3. **PDF Processing Errors:**
   ```bash
   # Test PDF manually
   python -c "
   import pdfplumber
   with pdfplumber.open('your_file.pdf') as pdf:
       print(len(pdf.pages))
   "
   ```

4. **Memory Issues:**
   ```bash
   # Reduce chunk size
   export CHUNK_SIZE=500
   
   # Process PDFs individually
   python ingestion.py --pdf_dir=./pdfs --force
   ```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
uvicorn app:app --reload --log-level debug
```

### Health Checks

```bash
# Check all endpoints
curl localhost:8000/api/health
curl localhost:8000/api/presets
curl -X POST localhost:8000/api/ask \
     -H "Content-Type: application/json" \
     -d '{"question": "test"}'
```

## Development

### Code Structure

```
backend/
├── app.py              # Main FastAPI application
├── ingestion.py        # PDF processing pipeline
├── chroma_client.py    # ChromaDB wrapper
├── embeddings_helper.py # Query processing utilities
├── prompt_templates.py # LLM prompt templates
├── requirements.txt    # Python dependencies
├── Dockerfile         # Container configuration
└── data/
    ├── chroma/        # ChromaDB storage
    └── product_map.json # Product mappings
```

### Adding New Features

1. **New API Endpoint:**
   ```python
   @app.post("/api/new-endpoint")
   async def new_endpoint():
       return {"message": "Hello"}
   ```

2. **New Preset:**
   ```python
   # Add to prompt_templates.py
   PRESET_QUESTIONS["new_puja"] = "Provide guidance for..."
   ```

3. **Custom Processing:**
   ```python
   # Extend ingestion.py
   def custom_text_processor(text):
       return processed_text
   ```

### Testing

```bash
# Unit tests
python -m pytest tests/

# Integration tests
python -m pytest tests/integration/

# Load testing
locust -f tests/load/locustfile.py
```

## Deployment

See `../infra/deploy_instructions.md` for detailed deployment guides to:

- Render
- Railway
- AWS ECS
- Google Cloud Run
- Docker Compose

## License

This project is part of the Puja AI Shopify Chatbot system. See main README for license information.
