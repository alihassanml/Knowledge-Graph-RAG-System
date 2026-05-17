# ⚡ Quick Start Guide

Get your Knowledge Graph RAG system running in 5 minutes!

## 1. Setup (1 minute)

```bash
# Navigate to project
cd "C:\Users\aliha\Documents\Deep Learning\Project\Knowledge Graph"

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 2. Configure (1 minute)

```bash
# Copy environment template
copy .env.example .env

# Edit .env and add your Groq API key
# Get free key: https://console.groq.com/keys
```

Your `.env` should look like:
```
GROQ_API_KEY=gsk_your_actual_key_here
```

## 3. Run Example (2 minutes)

```bash
# Run the main demo
python app.py
```

✅ This will:
- Create sample tech company data
- Extract entities and relationships
- Build a knowledge graph
- Answer test questions
- Generate interactive visualization (`knowledge_graph.html`)

## 4. Test the API (1 minute)

```bash
# In a new terminal
python fastapi_integration.py
```

Visit: **http://localhost:8000/docs**

### Quick API Test
```bash
# Upload and process documents
curl -X POST "http://localhost:8000/documents/add" \
  -H "Content-Type: application/json" \
  -d '{"content":"Apple was founded by Steve Jobs in California", "source":"test"}'

# Build graph
curl -X POST "http://localhost:8000/graph/build?graph_id=default"

# Query the graph
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query":"Who founded Apple and where?", "graph_id":"default"}'
```

## 📚 Next Steps

### Option 1: Use with Your Data
```python
from app import KnowledgeGraphBuilder

builder = KnowledgeGraphBuilder()
# Load your documents
docs = builder.load_documents("path/to/your/documents")
# Build and query
builder.build_knowledge_graph()
builder.setup_vector_store()
answer = builder.rag_query("Your question here")
```

### Option 2: Run Advanced Examples
```bash
python advanced_examples.py
```

### Option 3: Deploy as API
```bash
# Development
python fastapi_integration.py

# Production (using gunicorn)
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker fastapi_integration:app
```

## 🔑 Key Components

| Component | Purpose | File |
|-----------|---------|------|
| **KnowledgeGraphBuilder** | Core class for building graphs | `app.py` |
| **FastAPI Server** | REST API endpoints | `fastapi_integration.py` |
| **Examples** | Advanced use cases | `advanced_examples.py` |
| **Setup Guide** | Detailed documentation | `SETUP_GUIDE.md` |

## 🚀 Common Tasks

### Load Your Documents
```python
builder = KnowledgeGraphBuilder()
docs = builder.load_documents("./my_documents")
```

### Extract Entities
```python
entities, relations = builder.extract_entities_and_relations(text)
```

### Visualize Graph
```python
builder.visualize_graph("my_graph.html")  # Opens in browser
```

### Query RAG System
```python
answer = builder.rag_query("What's the relationship between X and Y?")
```

### Get Statistics
```python
print(f"Nodes: {builder.graph.number_of_nodes()}")
print(f"Edges: {builder.graph.number_of_edges()}")
```

## 🐛 Troubleshooting

**Problem:** `GROQ_API_KEY error`
```bash
# Make sure .env has your key
echo GROQ_API_KEY=gsk_xxx > .env
```

**Problem:** `Ollama embeddings not available`
```bash
# Install Ollama (optional, falls back gracefully)
# Download from https://ollama.ai
```

**Problem:** `JSON parsing errors`
- The model sometimes returns non-JSON responses (normal)
- System handles gracefully with fallback parsing
- Increase verbosity in logs if needed

## 📖 Documentation

- **Full Setup:** See `SETUP_GUIDE.md`
- **Advanced Use Cases:** See `advanced_examples.py`
- **API Endpoints:** Run API and visit `/docs`

## 🎯 Your Next Project

This setup works great as a foundation for:
- 📑 **Document Search** (like your FedSearch project)
- 🤖 **Conversational AI** (like your Adaptive-LLM project)
- 📊 **Data Analysis** (like your stock analysis project)
- 🔗 **Knowledge Bases** (enterprise wikis, docs)

## 💡 Pro Tips

1. **Use domain-specific documents** for better entity extraction
2. **Increase `chunk_size`** if you have longer documents
3. **Save your graphs** with `builder.save_graph()` for later use
4. **Monitor API logs** for debugging

## 📞 Need Help?

- Check `SETUP_GUIDE.md` for detailed guidance
- Review `advanced_examples.py` for code patterns
- Test individual components with `python app.py`

---

**Happy Knowledge Graphing! 🎉**

Built with ❤️ using Groq Qwen + LangChain
