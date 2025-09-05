# API Examples and Sample Flows

This document provides comprehensive examples of how to use the Puja AI Shopify Chatbot API, including curl commands, Postman collections, and complete workflow examples.

## 🚀 Quick Test Commands

### Health Check

```bash
curl -X GET http://localhost:8000/api/health
```

**Expected Response:**
```json
{
  "ok": true,
  "status": "healthy",
  "chroma_status": "ok",
  "openai_status": "ok",
  "timestamp": "2023-12-01T10:00:00Z"
}
```

### Get Available Presets

```bash
curl -X GET http://localhost:8000/api/presets
```

**Expected Response:**
```json
{
  "presets": [
    {
      "id": "ganesh",
      "name": "Ganesh Puja",
      "description": "Get guidance for Ganesh Puja"
    },
    {
      "id": "durga",
      "name": "Durga Puja", 
      "description": "Get guidance for Durga Puja"
    }
  ]
}
```

## 📝 Chat API Examples

### Example 1: Preset Button Flow

**Request:**
```bash
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{
    "puja_id": "ganesh",
    "question": "Ganesh Puja guidance"
  }'
```

**Expected Response:**
```json
{
  "ok": true,
  "response": {
    "summary": "Ganesh Puja for small home ceremony.",
    "steps": [
      {
        "step_no": 1,
        "title": "Prepare altar",
        "instruction": "Clean the area, place idol, light lamp"
      },
      {
        "step_no": 2,
        "title": "Offerings",
        "instruction": "Offer red flowers, incense, sweets."
      }
    ],
    "materials": [
      {
        "name": "incense",
        "quantity": "1 pack",
        "description": "Sandalwood or jasmine preferred",
        "product_match": "/products/incense-sticks"
      },
      {
        "name": "red flowers",
        "quantity": "1 garland",
        "product_match": "/collections/flowers"
      }
    ],
    "timings": ["Morning, day of Ganesh Chaturthi"],
    "mantras": ["Om Ganapataye Namah"],
    "sources": [
      {
        "book": "Ganesh Pooja Guide",
        "page": 14,
        "snippet": "...offer red flowers..."
      }
    ],
    "notes": "All steps are pulled directly from the indexed books."
  },
  "raw_llm_text": "{\n  \"summary\": \"Ganesh Puja for small home ceremony.\",\n  ...",
  "sources": [...],
  "cost_estimate": {
    "input_cost": 0.0012,
    "output_cost": 0.0008,
    "total_cost": 0.002,
    "prompt_tokens": 800,
    "completion_tokens": 400
  },
  "cache_hit": false
}
```

### Example 2: Free Text Flow

**Request:**
```bash
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How to perform Lakshmi Puja on Diwali?",
    "user_id": "user123"
  }'
```

**Expected Response:**
```json
{
  "ok": true,
  "response": {
    "summary": "Lakshmi Puja procedure for Diwali celebration",
    "steps": [
      {
        "step_no": 1,
        "title": "Cleaning and Preparation",
        "instruction": "Clean the entire house, especially the entrance and prayer area"
      },
      {
        "step_no": 2,
        "title": "Altar Setup",
        "instruction": "Place Lakshmi idol or picture on a clean cloth, arrange kalash with water"
      },
      {
        "step_no": 3,
        "title": "Lighting Diyas",
        "instruction": "Light oil lamps around the house, especially at entrance and windows"
      }
    ],
    "materials": [
      {
        "name": "oil lamps (diyas)",
        "quantity": "21 pieces",
        "description": "Clay lamps with cotton wicks",
        "product_match": "/products/clay-diyas-set"
      },
      {
        "name": "lotus flowers",
        "quantity": "5-7 flowers",
        "product_match": "/products/fresh-lotus"
      },
      {
        "name": "sweets",
        "quantity": "Assorted",
        "description": "Laddu, barfi, or kheer",
        "product_match": "/collections/diwali-sweets"
      }
    ],
    "timings": [
      "Evening during Diwali",
      "Amavasya night is most auspicious",
      "Between 6 PM to 8 PM"
    ],
    "mantras": [
      "Om Shreem Mahalakshmyai Namaha",
      "Mahalakshmi Ashtakam"
    ],
    "sources": [
      {
        "book": "Lakshmi Puja Complete Guide",
        "page": 45,
        "snippet": "On Diwali night, goddess Lakshmi visits clean and well-lit homes..."
      }
    ],
    "notes": "Ensure the house remains clean and well-lit throughout the night for Goddess Lakshmi's blessings."
  },
  "cache_hit": false
}
```

### Example 3: Error Response

**Request with Invalid Preset:**
```bash
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{
    "puja_id": "invalid_puja",
    "question": "Invalid puja"
  }'
```

**Expected Error Response:**
```json
{
  "ok": false,
  "error": "Unknown puja_id: invalid_puja",
  "response": null
}
```

## 🔐 Admin API Examples

### Upload PDF

```bash
curl -X POST http://localhost:8000/api/upload-pdf \
  -H "Authorization: Bearer your_admin_api_key_here" \
  -F "file=@sample_puja_guide.pdf"
```

**Expected Response:**
```json
{
  "ok": true,
  "message": "Successfully processed sample_puja_guide.pdf",
  "filename": "sample_puja_guide.pdf",
  "chunks_created": 45
}
```

### Get System Statistics

```bash
curl -X GET http://localhost:8000/api/stats \
  -H "Authorization: Bearer your_admin_api_key_here"
```

**Expected Response:**
```json
{
  "cache_entries": 12,
  "rate_limit_entries": 5,
  "product_mappings": 89,
  "collection_name": "puja_books",
  "document_count": 1247,
  "persist_dir": "./data/chroma"
}
```

### Clear Cache

```bash
curl -X DELETE http://localhost:8000/api/cache \
  -H "Authorization: Bearer your_admin_api_key_here"
```

**Expected Response:**
```json
{
  "ok": true,
  "message": "Cleared 12 cache entries"
}
```

### Trigger Reindexing

```bash
curl -X POST http://localhost:8000/api/reindex \
  -H "Authorization: Bearer your_admin_api_key_here"
```

**Expected Response:**
```json
{
  "ok": true,
  "message": "Reindexing completed",
  "stats": {
    "num_pdfs": 5,
    "total_chunks": 1247,
    "average_chunks_per_pdf": 249.4,
    "errors": []
  }
}
```

## 🔄 Complete Workflow Examples

### Workflow 1: New User Journey

1. **User visits Shopify store with widget**
2. **Clicks Ganesh Puja preset**
3. **Receives structured guidance**
4. **Clicks product links to purchase materials**

```bash
# Step 1: Get available presets
curl -X GET http://localhost:8000/api/presets

# Step 2: User selects Ganesh Puja
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{
    "puja_id": "ganesh",
    "user_id": "new_user_123"
  }'

# Step 3: User asks follow-up question
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What time is best for Ganesh Puja?",
    "user_id": "new_user_123"
  }'
```

### Workflow 2: Admin Content Management

1. **Admin uploads new PDF**
2. **System processes and indexes content**
3. **Admin verifies new content is searchable**

```bash
# Step 1: Upload new PDF
curl -X POST http://localhost:8000/api/upload-pdf \
  -H "Authorization: Bearer admin_key_123" \
  -F "file=@new_puja_guide.pdf"

# Step 2: Check system stats
curl -X GET http://localhost:8000/api/stats \
  -H "Authorization: Bearer admin_key_123"

# Step 3: Test new content
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Content from the new PDF guide"
  }'
```

### Workflow 3: Cache Performance Testing

```bash
# First request (cache miss)
time curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"puja_id": "ganesh"}' 

# Second identical request (cache hit)
time curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"puja_id": "ganesh"}'

# Check cache stats
curl -X GET http://localhost:8000/api/stats \
  -H "Authorization: Bearer admin_key_123"
```

## 📊 Postman Collection

### Collection JSON

Save this as `puja-ai-postman-collection.json`:

```json
{
  "info": {
    "name": "Puja AI Shopify Chatbot",
    "description": "Complete API collection for Puja AI backend",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    {
      "key": "baseUrl",
      "value": "http://localhost:8000",
      "type": "string"
    },
    {
      "key": "adminApiKey",
      "value": "your_admin_api_key_here",
      "type": "string"
    }
  ],
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{baseUrl}}/api/health",
          "host": ["{{baseUrl}}"],
          "path": ["api", "health"]
        }
      }
    },
    {
      "name": "Get Presets",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{baseUrl}}/api/presets",
          "host": ["{{baseUrl}}"],
          "path": ["api", "presets"]
        }
      }
    },
    {
      "name": "Ask Question - Preset",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n    \"puja_id\": \"ganesh\",\n    \"question\": \"Ganesh Puja guidance\",\n    \"user_id\": \"test_user\"\n}"
        },
        "url": {
          "raw": "{{baseUrl}}/api/ask",
          "host": ["{{baseUrl}}"],
          "path": ["api", "ask"]
        }
      }
    },
    {
      "name": "Ask Question - Free Text",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n    \"question\": \"How to perform Lakshmi Puja?\",\n    \"user_id\": \"test_user\"\n}"
        },
        "url": {
          "raw": "{{baseUrl}}/api/ask",
          "host": ["{{baseUrl}}"],
          "path": ["api", "ask"]
        }
      }
    },
    {
      "name": "Upload PDF (Admin)",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{adminApiKey}}"
          }
        ],
        "body": {
          "mode": "formdata",
          "formdata": [
            {
              "key": "file",
              "type": "file",
              "src": "sample.pdf"
            }
          ]
        },
        "url": {
          "raw": "{{baseUrl}}/api/upload-pdf",
          "host": ["{{baseUrl}}"],
          "path": ["api", "upload-pdf"]
        }
      }
    },
    {
      "name": "Get Stats (Admin)",
      "request": {
        "method": "GET",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{adminApiKey}}"
          }
        ],
        "url": {
          "raw": "{{baseUrl}}/api/stats",
          "host": ["{{baseUrl}}"],
          "path": ["api", "stats"]
        }
      }
    }
  ]
}
```

### Import Instructions

1. Open Postman
2. Click "Import" 
3. Upload the JSON file
4. Set environment variables:
   - `baseUrl`: Your backend URL
   - `adminApiKey`: Your admin API key

## 🧪 Testing Scenarios

### Load Testing

```bash
# Install hey (HTTP load testing tool)
# brew install hey  # macOS
# apt-get install hey  # Ubuntu

# Test concurrent requests
hey -n 100 -c 10 -m POST \
  -H "Content-Type: application/json" \
  -d '{"puja_id": "ganesh"}' \
  http://localhost:8000/api/ask
```

### Rate Limiting Test

```bash
# Test rate limiting (should fail after 60 requests)
for i in {1..65}; do
  echo "Request $i"
  curl -X POST http://localhost:8000/api/ask \
    -H "Content-Type: application/json" \
    -d '{"question": "test"}' \
    -w "Status: %{http_code}\n"
  sleep 0.5
done
```

### Error Handling Tests

```bash
# Test invalid JSON
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d 'invalid json'

# Test missing fields
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{}'

# Test unauthorized admin endpoint
curl -X GET http://localhost:8000/api/stats
```

## 🔍 Debugging Commands

### Check ChromaDB Status

```bash
# Health check with detailed output
curl -X GET http://localhost:8000/api/health | jq '.'

# Check collection info (admin)
curl -X GET http://localhost:8000/api/stats \
  -H "Authorization: Bearer your_api_key" | jq '.collection_name, .document_count'
```

### Verify PDF Processing

```bash
# Test ingestion locally
cd backend/
python ingestion.py --pdf_dir=./pdfs

# Upload via API
curl -X POST http://localhost:8000/api/upload-pdf \
  -H "Authorization: Bearer your_api_key" \
  -F "file=@test.pdf" | jq '.'
```

### Monitor API Performance

```bash
# Time API responses
time curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "quick test"}'

# Check cache performance
curl -X GET http://localhost:8000/api/stats \
  -H "Authorization: Bearer your_api_key" | jq '.cache_entries'
```

## 📱 Frontend Integration Examples

### JavaScript Fetch

```javascript
// Basic question
const response = await fetch('http://localhost:8000/api/ask', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    question: 'How to perform Ganesh Puja?',
    user_id: 'user123'
  })
});

const data = await response.json();
console.log(data.response);
```

### React Component

```jsx
import { useState } from 'react';

function PujaChat() {
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);

  const askQuestion = async (question) => {
    setLoading(true);
    try {
      const res = await fetch('/api/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question })
      });
      const data = await res.json();
      setResponse(data.response);
    } catch (error) {
      console.error('Error:', error);
    }
    setLoading(false);
  };

  return (
    <div>
      <button onClick={() => askQuestion('Ganesh Puja guide')}>
        Get Ganesh Puja Guide
      </button>
      {loading && <p>Loading...</p>}
      {response && (
        <div>
          <h3>{response.summary}</h3>
          <ul>
            {response.steps?.map((step, i) => (
              <li key={i}>{step.instruction}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
```

## 🚨 Error Codes and Responses

### HTTP Status Codes

- **200**: Success
- **400**: Bad Request (invalid input)
- **401**: Unauthorized (missing/invalid API key)
- **429**: Too Many Requests (rate limit exceeded)
- **500**: Internal Server Error

### Error Response Format

```json
{
  "ok": false,
  "error": "Error description",
  "response": null,
  "sources": null
}
```

### Common Error Messages

- `"Unknown puja_id: xyz"` - Invalid preset ID
- `"No relevant information found in source books"` - Query didn't match any content
- `"Rate limit exceeded"` - Too many requests from IP
- `"API key required"` - Admin endpoint without authentication
- `"ChromaDB not available"` - Database connection issue

This completes the comprehensive API examples and testing guide for the Puja AI Shopify Chatbot system.
