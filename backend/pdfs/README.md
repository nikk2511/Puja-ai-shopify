# PDF Source Documents

This directory should contain the Hindu puja and worship guide PDF files that will be processed by the ingestion pipeline.

## 📚 Recommended PDF Content

For optimal results, include PDFs covering:

### Core Puja Guides
- **Ganesh Puja** - Complete procedures and materials
- **Durga Puja** - Navratri and Durga worship
- **Lakshmi Puja** - Diwali and wealth deity worship
- **Saraswati Puja** - Knowledge and learning deity worship
- **Shiva Puja** - Lord Shiva worship procedures
- **Vishnu Puja** - Lord Vishnu and avatar worship

### Festival Celebrations
- **Diwali** - Festival of lights procedures
- **Navratri** - Nine nights celebration
- **Holi** - Color festival rituals
- **Janmashtami** - Krishna's birthday celebration
- **Ram Navami** - Lord Rama's birthday

### Daily Worship
- **Home Puja** - Daily worship routines
- **Morning Prayers** - Sandhya Vandana
- **Evening Aarti** - Evening prayers
- **Mantra Collections** - Sacred chants and hymns

### Special Ceremonies
- **Satyanarayan Puja** - Monthly worship ceremony
- **Griha Pravesh** - Housewarming rituals
- **Vastu Puja** - Home blessing ceremonies

## 📋 PDF Requirements

### Format Requirements
- **Text-based PDFs** (preferred for best extraction)
- **OCR PDFs** (scanned documents with text layer)
- **Language**: English or English transliteration
- **File size**: No specific limit (will be automatically chunked)

### Content Quality
- **Clear structure** with headings and sections
- **Step-by-step procedures** clearly outlined
- **Material lists** with specific items
- **Timing information** and auspicious dates
- **Mantra texts** in readable format
- **Source attributions** when possible

### Naming Convention
Use descriptive filenames:
- `Ganesh_Puja_Complete_Guide.pdf`
- `Diwali_Celebration_Manual.pdf`
- `Daily_Home_Worship_Procedures.pdf`
- `Mantra_Collection_Sanskrit_English.pdf`

## 🚀 Processing Instructions

### Adding New PDFs

1. **Place PDF files** in this directory
2. **Run ingestion** to process new content:
   ```bash
   cd backend/
   python ingestion.py --pdf_dir=./pdfs
   ```
3. **Verify processing** by checking the logs and ChromaDB collection

### Re-processing PDFs

To force re-processing of all PDFs:
```bash
python ingestion.py --pdf_dir=./pdfs --force
```

### Upload via API

Alternatively, upload PDFs via the admin API:
```bash
curl -X POST http://localhost:8000/api/upload-pdf \
     -H "Authorization: Bearer your_admin_api_key" \
     -F "file=@your_puja_guide.pdf"
```

## ⚠️ Important Notes

### Copyright and Sources
- **Only include PDFs** you have rights to use
- **Respect copyright** and intellectual property
- **Attribute sources** properly in your documentation
- **Traditional texts** and public domain content preferred

### Content Accuracy
- **Verify authenticity** of sources before processing
- **Traditional sources** are preferred over modern interpretations
- **Multiple sources** for the same puja provide better coverage
- **Regional variations** should be noted when possible

### Processing Results
After processing, each PDF will be:
- **Text extracted** page by page
- **Cleaned** of headers/footers and artifacts
- **Chunked** into 1000-character segments
- **Embedded** using OpenAI text-embedding-3-small
- **Stored** in ChromaDB with metadata

## 📊 Expected Results

With 15-20 quality PDF sources, you should achieve:
- **1000-2000 chunks** of indexed content
- **Comprehensive coverage** of major puja types
- **Detailed step-by-step** procedures
- **Material recommendations** with quantities
- **Timing and astrological** guidance
- **Mantra and chant** collections

## 🔍 Testing Your Content

After processing, test the knowledge base:
```bash
# Test basic coverage
curl -X POST http://localhost:8000/api/ask \
     -H "Content-Type: application/json" \
     -d '{"puja_id": "ganesh"}'

# Test specific content
curl -X POST http://localhost:8000/api/ask \
     -H "Content-Type: application/json" \
     -d '{"question": "What materials needed for Lakshmi Puja?"}'
```

## 📝 Sample PDF Sources

While we cannot provide copyrighted content, consider these types of sources:

### Traditional Texts (Public Domain)
- Classical Agama texts
- Traditional Puja Paddhati
- Ancient worship manuals
- Stotra and mantra collections

### Modern Guides (With Permission)
- Temple publication guides
- Religious organization manuals
- Educational institution materials
- Community worship guides

### Academic Sources
- University religious studies materials
- Scholarly translations of texts
- Anthropological studies of rituals
- Comparative religion resources

## 🤝 Contributing Sources

If you have quality PDF sources to contribute:
1. Verify you have distribution rights
2. Ensure content accuracy and authenticity  
3. Add descriptive metadata
4. Test processed results
5. Submit through appropriate channels

---

**Place your PDF files in this directory and run the ingestion pipeline to begin building your Hindu puja knowledge base!**
