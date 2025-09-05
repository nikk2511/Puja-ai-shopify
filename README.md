# Puja AI Shopify Chatbot

A complete AI-powered chatbot system for Shopify stores that provides Hindu puja and ritual guidance using Retrieval-Augmented Generation (RAG) with OpenAI and ChromaDB.

## 🌟 Features

- **📚 PDF Knowledge Base** - Ingests 15-20 PDF books on Hindu puja and worship
- **🤖 AI-Powered Responses** - Uses OpenAI GPT-4o-mini with RAG for accurate guidance  
- **🔍 Semantic Search** - ChromaDB vector storage with text-embedding-3-small
- **🛒 Shopify Integration** - Product recommendations with direct purchase links
- **📱 Multiple Interfaces** - Next.js web app + embeddable JavaScript widget
- **⚡ Real-time Chat** - Instant responses with structured guidance
- **🎯 Preset Questions** - 20 common puja types for quick access
- **📖 Source Attribution** - All responses cite original text sources
- **🐳 Docker Ready** - Complete containerization for easy deployment

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** and **Node.js 18+**
- **OpenAI API key** (for embeddings and chat completion)
- **PDF files** containing Hindu puja guides (place in `backend/pdfs/`)

### 1. Backend Setup

```bash
cd backend/

# Install dependencies
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp env_example.txt .env
# Edit .env with your OpenAI API key

# Create directories
mkdir -p pdfs data/chroma

# Add your PDF files to pdfs/ directory
# Then run ingestion
python ingestion.py --pdf_dir=./pdfs

# Start backend server
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend Setup

```bash
cd frontend/

# Install dependencies
npm install

# Configure environment
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start development server
npm run dev
```

### 3. Access the Application

- **Web App:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/api/health

## 📁 Project Structure

```
puja-ai-shopify/
├─ backend/                 # Python FastAPI backend
│  ├─ app.py               # Main FastAPI application
│  ├─ ingestion.py         # PDF processing pipeline
│  ├─ chroma_client.py     # ChromaDB wrapper
│  ├─ embeddings_helper.py # Query processing utilities
│  ├─ prompt_templates.py  # LLM prompt templates
│  ├─ requirements.txt     # Python dependencies
│  ├─ Dockerfile          # Backend container
│  ├─ .env.example        # Environment template
│  └─ data/
│     ├─ chroma/          # ChromaDB storage
│     └─ product_map.json # Shopify product mappings
├─ frontend/               # Next.js frontend
│  ├─ app/
│  │  ├─ page.jsx         # Main application page
│  │  ├─ layout.js        # App layout and metadata
│  │  ├─ globals.css      # Global styles
│  │  └─ components/
│  │     ├─ PujaWidget.jsx     # Main chatbot widget
│  │     ├─ PresetButtons.jsx  # Preset puja options
│  │     ├─ ChatInput.jsx      # Text input component
│  │     └─ AnswerDisplay.jsx  # Response display
│  ├─ public/embed.js     # Embeddable widget
│  ├─ package.json        # Frontend dependencies
│  └─ next.config.js      # Next.js configuration
├─ infra/                  # Infrastructure and deployment
│  ├─ docker-compose.yml  # Docker orchestration
│  └─ deploy_instructions.md # Deployment guides
└─ README.md              # This file
```

## 🔧 Configuration

### Backend Environment (.env)

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

# Performance
MAX_TOKENS=1500
TEMPERATURE=0.0
```

### Frontend Environment (.env.local)

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🛒 Shopify Integration

### Method 1: Embeddable Widget (Simplest)

Add to your Shopify theme:

```html
<!-- In theme.liquid before </body> -->
<script>
  window.pujaAIConfig = {
    apiUrl: 'https://your-backend-url.com',
    position: 'bottom-right',
    theme: 'light'
  };
</script>
<script src="https://your-frontend-url.com/embed.js"></script>
```

### Method 2: Shopify App

1. Create Shopify Partner account
2. Create new app with your frontend URL
3. Implement OAuth flow (see frontend README)
4. Install in Shopify stores

### Method 3: Script Tag API

```bash
curl -X POST "https://shop.myshopify.com/admin/api/2023-10/script_tags.json" \
  -H "X-Shopify-Access-Token: YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"script_tag": {"event": "onload", "src": "https://your-domain.com/embed.js"}}'
```

## 📚 API Usage Examples

### Basic Chat Request

```bash
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How to perform Ganesh Puja at home?"
  }'
```

### Preset Puja Request

```bash
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{
    "puja_id": "ganesh",
    "question": "Ganesh Puja guidance"
  }'
```

### Get Available Presets

```bash
curl http://localhost:8000/api/presets
```

### Upload PDF (Admin)

```bash
curl -X POST http://localhost:8000/api/upload-pdf \
  -H "Authorization: Bearer your_api_key_here" \
  -F "file=@your_puja_guide.pdf"
```

## 📖 Sample Response Structure

```json
{
  "ok": true,
  "response": {
    "summary": "Ganesh Puja for small home ceremony",
    "steps": [
      {
        "step_no": 1,
        "title": "Preparation",
        "instruction": "Clean the worship area and arrange the altar"
      },
      {
        "step_no": 2,
        "title": "Invocation",
        "instruction": "Place Ganesh idol and light incense"
      }
    ],
    "materials": [
      {
        "name": "incense sticks",
        "quantity": "5-7 sticks",
        "description": "Sandalwood or jasmine preferred",
        "product_match": "/products/sandalwood-incense"
      },
      {
        "name": "red flowers",
        "quantity": "1 garland",
        "product_match": "/collections/puja-flowers"
      }
    ],
    "timings": [
      "Early morning (6-8 AM)",
      "Wednesday is most auspicious"
    ],
    "mantras": [
      "Om Ganapataye Namah",
      "Vakratunda Mahakaya Suryakoti Samaprabha"
    ],
    "sources": [
      {
        "book": "Complete Guide to Ganesh Puja",
        "page": 23,
        "snippet": "The idol should be placed facing east for maximum benefit..."
      }
    ],
    "notes": "For important occasions, consult a local priest for specific timings and additional rituals."
  },
  "cache_hit": false,
  "cost_estimate": {
    "total_cost": 0.001247
  }
}
```

## 🐳 Docker Deployment

### Development with Docker Compose

```bash
cd infra/
cp ../backend/env_example.txt .env
# Edit .env with your API keys

docker-compose up -d
```

### Production Deployment

```bash
# Build backend
docker build -t puja-ai-backend ./backend/

# Run with environment
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  puja-ai-backend
```

## 🌐 Deployment Options

### Backend Deployment

- **Render:** One-click deployment from GitHub
- **Railway:** `railway deploy` command
- **AWS ECS:** Container service with load balancing
- **Google Cloud Run:** Serverless container platform
- **DigitalOcean:** App Platform deployment

### Frontend Deployment

- **Vercel:** Next.js optimized hosting (recommended)
- **Netlify:** Static site hosting
- **AWS S3 + CloudFront:** Static hosting with CDN
- **GitHub Pages:** Free static hosting

See `infra/deploy_instructions.md` for detailed guides.

## 🔧 Development

### Adding New Puja Types

1. **Add to preset questions:**
   ```python
   # In backend/prompt_templates.py
   PRESET_QUESTIONS["new_puja"] = "Provide step-by-step procedure for..."
   ```

2. **Add icon mapping:**
   ```javascript
   // In frontend/app/components/PresetButtons.jsx
   const PRESET_ICONS = {
     "new_puja": "🕉️"
   }
   ```

### Customizing Product Mapping

```json
// In backend/data/product_map.json
{
  "coconut": "/products/fresh-coconut",
  "incense": "/products/premium-incense-sticks",
  "flowers": "/collections/puja-flowers"
}
```

### Adding New PDF Sources

1. Place PDF in `backend/pdfs/`
2. Run: `python ingestion.py --pdf_dir=./pdfs --force`
3. Verify: Check ChromaDB collection count

## 🧪 Testing

### Backend Testing

```bash
cd backend/

# Unit tests
python -m pytest tests/

# Test ingestion
python ingestion.py --pdf_dir=./test_pdfs

# Test API endpoints
python -m pytest tests/test_api.py -v
```

### Frontend Testing

```bash
cd frontend/

# Lint and type check
npm run lint
npx tsc --noEmit

# Test build
npm run build
```

### Integration Testing

```bash
# Test full flow
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Test question"}'
```

## 📊 Monitoring and Analytics

### Built-in Metrics

- **API Usage:** Request count, response times
- **Cache Performance:** Hit/miss ratios
- **OpenAI Costs:** Token usage and cost estimation
- **ChromaDB Stats:** Collection size, query performance

### Health Monitoring

```bash
# Health check endpoint
curl http://localhost:8000/api/health

# System stats (admin)
curl -H "Authorization: Bearer your_api_key" \
     http://localhost:8000/api/stats
```

## 🛡️ Security

### API Security

- **Rate Limiting:** 60 requests/minute per IP
- **API Key Auth:** Admin endpoints require authentication
- **CORS:** Configurable origin restrictions
- **Input Validation:** Pydantic models for request validation

### Data Privacy

- **No PII Storage:** User questions are not logged by default
- **Cache Management:** Automatic cache expiration
- **Source Attribution:** All responses cite original sources
- **GDPR Compliance:** Optional user data deletion endpoints

## 🔍 Troubleshooting

### Common Issues

1. **ChromaDB Permission Errors:**
   ```bash
   chmod -R 755 backend/data/chroma/
   ```

2. **OpenAI API Errors:**
   ```bash
   # Check API key validity
   curl https://api.openai.com/v1/models \
        -H "Authorization: Bearer $OPENAI_API_KEY"
   ```

3. **CORS Issues:**
   ```python
   # Update CORS origins in backend/app.py
   allow_origins=["https://your-domain.com"]
   ```

4. **PDF Processing Fails:**
   ```bash
   # Test PDF manually
   python -c "import pdfplumber; print(pdfplumber.open('test.pdf').pages[0].extract_text())"
   ```

### Debug Mode

```bash
# Backend debug logging
export LOG_LEVEL=DEBUG
uvicorn app:app --reload --log-level debug

# Frontend debug
export NODE_ENV=development
npm run dev
```

## 📄 Sample Data

### Test PDFs

For testing, you can use sample PDF content about:

- Basic puja procedures
- Festival celebrations (Diwali, Navratri, etc.)
- Daily worship routines
- Mantra collections
- Ritual significance explanations

### Sample Questions

- "How do I perform Ganesh Puja at home?"
- "What materials do I need for Lakshmi Puja?"
- "What are the steps for Diwali celebration?"
- "How to do morning aarti?"
- "What mantras should I chant during Shiva Puja?"

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Development Guidelines

- Follow Python PEP 8 for backend code
- Use ESLint configuration for frontend
- Add comprehensive docstrings
- Include unit tests for new features
- Update documentation

## 📜 License

This project is licensed under the MIT License. See LICENSE file for details.

## ⚠️ Disclaimer

This AI assistant provides guidance based on traditional Hindu texts and should be used for educational purposes. For important religious ceremonies, please consult with qualified priests or religious authorities.

## 🙏 Acknowledgments

- OpenAI for language models and embeddings
- ChromaDB for vector database functionality
- Shopify for e-commerce platform integration
- The Hindu community for preserving sacred texts

## 📞 Support

For support and questions:

1. Check the troubleshooting section above
2. Review component-specific README files
3. Create GitHub issues for bugs
4. Join our community discussions

---

**Built with ❤️ for the Hindu community and Shopify merchants**
