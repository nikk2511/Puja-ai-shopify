# Deployment Instructions for Puja AI Shopify Chatbot

This document provides step-by-step instructions for deploying the Puja AI Shopify Chatbot to various platforms.

## Prerequisites

- Docker and Docker Compose installed
- OpenAI API key
- PDF files for ingestion (place in `backend/pdfs/` directory)
- Git repository (for cloud deployments)

## Local Development Deployment

### Using Docker Compose

1. **Set up environment variables:**
   ```bash
   cd infra/
   cp ../backend/env_example.txt .env
   # Edit .env file with your actual API keys
   ```

2. **Build and run:**
   ```bash
   docker-compose up -d
   ```

3. **Check health:**
   ```bash
   curl http://localhost:8000/api/health
   ```

4. **Upload and ingest PDFs:**
   ```bash
   # Place PDFs in backend/pdfs/ directory
   # Then trigger reindexing
   curl -X POST http://localhost:8000/api/reindex \
        -H "Authorization: Bearer your-api-key"
   ```

### Manual Local Setup

1. **Backend setup:**
   ```bash
   cd backend/
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp env_example.txt .env
   # Edit .env with your API keys
   ```

2. **Run ingestion:**
   ```bash
   python ingestion.py --pdf_dir=./pdfs
   ```

3. **Start backend:**
   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Frontend setup:**
   ```bash
   cd ../frontend/
   npm install
   npm run dev
   ```

## Cloud Deployment Options

### Deploy to Render

1. **Create Render account** at https://render.com

2. **Create new Web Service:**
   - Connect your GitHub repository
   - Choose the backend directory as root
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app:app --host 0.0.0.0 --port $PORT`

3. **Set environment variables in Render dashboard:**
   ```
   OPENAI_API_KEY=your_key_here
   OPENAI_EMBED_MODEL=text-embedding-3-small
   OPENAI_CHAT_MODEL=gpt-4o-mini
   CHROMA_PERSIST_DIR=/opt/render/project/src/data/chroma
   CHROMA_COLLECTION_NAME=puja_books
   FASTAPI_HOST=0.0.0.0
   FASTAPI_PORT=8000
   API_KEY=your_admin_key_here
   ```

4. **Deploy and test:**
   - Render will automatically deploy
   - Test: `https://your-app.onrender.com/api/health`

### Deploy to Railway

1. **Create Railway account** at https://railway.app

2. **Deploy from GitHub:**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login and deploy
   railway login
   railway deploy
   ```

3. **Set environment variables:**
   ```bash
   railway variables set OPENAI_API_KEY=your_key_here
   railway variables set CHROMA_PERSIST_DIR=/app/data/chroma
   # ... set other variables
   ```

### Deploy Frontend to Vercel

1. **Create Vercel account** at https://vercel.com

2. **Deploy frontend:**
   ```bash
   cd frontend/
   npx vercel
   ```

3. **Set environment variables:**
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.com
   ```

### Deploy to AWS ECS (Advanced)

1. **Build and push Docker image:**
   ```bash
   # Build image
   docker build -t puja-ai-backend ./backend/
   
   # Tag for ECR
   docker tag puja-ai-backend:latest your-account.dkr.ecr.region.amazonaws.com/puja-ai-backend:latest
   
   # Push to ECR
   docker push your-account.dkr.ecr.region.amazonaws.com/puja-ai-backend:latest
   ```

2. **Create ECS service with task definition:**
   - Use the pushed image
   - Set environment variables
   - Configure load balancer
   - Set up persistent storage for ChromaDB

### Deploy to Google Cloud Run

1. **Build and deploy:**
   ```bash
   cd backend/
   
   # Deploy to Cloud Run
   gcloud run deploy puja-ai-backend \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars OPENAI_API_KEY=your_key,CHROMA_PERSIST_DIR=/app/data
   ```

## Production Considerations

### Security
- Use proper CORS settings for your domain
- Set up API rate limiting
- Use environment-specific API keys
- Enable HTTPS
- Set up proper authentication for admin endpoints

### Performance
- Use Redis for caching (uncomment in docker-compose.yml)
- Set up CDN for static assets
- Consider using a managed vector database (Pinecone) for scale
- Monitor API usage and costs

### Monitoring
- Set up health check endpoints
- Monitor ChromaDB storage usage
- Track API response times
- Set up alerts for failures

### Data Management
- Regular backups of ChromaDB data
- PDF file management strategy
- Log rotation and management
- Cost monitoring for OpenAI usage

## Shopify Integration

### Shopify App Setup

1. **Create Shopify Partner account**
2. **Create new app in Partner Dashboard**
3. **Set app URL to your deployed frontend**
4. **Configure webhooks if needed**

### Embedded App (Advanced)
For full Shopify app integration:
1. Implement OAuth flow
2. Use Shopify App Bridge
3. Set up app installation process
4. Configure app permissions

### Simple Widget Integration
For basic integration:
1. Use the embeddable widget (`frontend/public/embed.js`)
2. Add script tag to Shopify theme
3. Customize styling to match store theme

## Troubleshooting

### Common Issues

1. **ChromaDB permission errors:**
   ```bash
   # Fix permissions
   chmod -R 755 backend/data/
   ```

2. **OpenAI API errors:**
   - Check API key validity
   - Monitor usage limits
   - Verify model availability

3. **PDF processing fails:**
   - Check PDF file integrity
   - Ensure PDFs contain extractable text
   - Try different PDF processing libraries

4. **Docker build issues:**
   ```bash
   # Clean Docker cache
   docker system prune -a
   
   # Rebuild without cache
   docker-compose build --no-cache
   ```

### Logs and Debugging

```bash
# View Docker logs
docker-compose logs -f puja-ai-backend

# Check health endpoint
curl -v http://localhost:8000/api/health

# Test ingestion
curl -X POST http://localhost:8000/api/ask \
     -H "Content-Type: application/json" \
     -d '{"question": "How to perform Ganesh Puja?"}'
```

## Scaling Considerations

- **Horizontal scaling:** Use load balancer with multiple instances
- **Database scaling:** Consider Pinecone or other managed vector DBs
- **Caching:** Implement Redis for better performance
- **CDN:** Use CDN for static assets and API responses
- **Monitoring:** Set up proper monitoring and alerting

## Maintenance

- Regular dependency updates
- ChromaDB data backups
- API usage monitoring
- Performance optimization
- Security updates
