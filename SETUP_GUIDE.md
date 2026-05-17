# Knowledge Graph RAG System with Groq Qwen Model

A production-ready system for building knowledge graphs and performing Retrieval-Augmented Generation (RAG) using Groq's Qwen model with hybrid retrieval capabilities.

## Features

✨ **Hybrid Retrieval System**
- Vector Search (semantic similarity with Ollama embeddings)
- Keyword Search (full-text matching)
- Graph Traversal (entity relationship navigation)

🤖 **Groq Qwen Integration**
- Fast inference with Groq's API
- Qwen 2 7B model for entity/relationship extraction
- Low-latency responses

📊 **Knowledge Graph**
- Automatic entity extraction (PERSON, ORGANIZATION, LOCATION, CONCEPT)
- Relationship discovery
- Interactive visualization with PyVis
- JSON export for integration

## Installation

### 1. Clone and Setup
```bash
cd "C:\Users\aliha\Documents\Deep Learning\Project\Knowledge Graph"
python -m venv venv
venv\Scripts\activate  # On Windows
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Environment Variables
```bash
# Copy the example file
copy .env.example .env

# Edit .env and add your Groq API key
# Get free API key: https://console.groq.com/keys
```

### 4. (Optional) Install Ollama for Local Embeddings
```bash
# Download from https://ollama.ai
# Then pull the embedding model:
ollama pull nomic-embed-text
```

## Quick Start

### Basic Usage
```python
from app import KnowledgeGraphBuilder

# Initialize
builder = KnowledgeGraphBuilder()

# Load documents
documents = builder.load_documents("path/to/documents")

# Build knowledge graph
builder.build_knowledge_graph()

# Setup vector store
builder.setup_vector_store()

# Ask a question
answer = builder.rag_query("Who founded Apple and where?")
print(answer)

# Visualize the graph
builder.visualize_graph()

# Save graph
builder.save_graph("my_knowledge_graph.json")
```

### Run Complete Example
```bash
python app.py
```

This will:
1. Create sample data (tech companies)
2. Extract entities and relationships
3. Build the knowledge graph
4. Generate an interactive visualization (`knowledge_graph.html`)
5. Answer test queries using RAG

## Architecture

### KnowledgeGraphBuilder Class

**Methods:**
- `load_documents(source)` - Load from file or directory
- `extract_entities_and_relations(text)` - Use Groq Qwen to extract entities
- `build_knowledge_graph()` - Create graph from documents
- `setup_vector_store(documents)` - Initialize Chroma vector store
- `hybrid_retrieve(query)` - Combine 3 retrieval methods
- `rag_query(query)` - Generate answer from context
- `visualize_graph(output_file)` - Create interactive HTML visualization
- `save_graph(filepath)` - Export as JSON

### Retrieval Pipeline

```
User Query
    ↓
1. Vector Search (Semantic matching via embeddings)
2. Keyword Search (Full-text matching)
3. Graph Traversal (Entity relationships)
    ↓
Combined Context
    ↓
Groq Qwen Model (RAG Generation)
    ↓
Answer
```

## Configuration

### Groq Model Selection
Currently using `qwen2-7b-32b`. Alternative Qwen models on Groq:
- `qwen-7b`
- `qwen-32b`

Update in `app.py` line ~48:
```python
self.llm = ChatGroq(
    model="qwen2-7b-32b",  # Change this
    temperature=0.3,
    groq_api_key=self.groq_api_key,
)
```

### Vector Store Options
The system uses Chroma with Ollama embeddings. For alternatives:
```python
# HuggingFace embeddings (offline)
from langchain.embeddings import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings()

# OpenAI embeddings (requires API key)
from langchain.embeddings import OpenAIEmbeddings
embeddings = OpenAIEmbeddings()
```

## Your GitHub Repositories Reference

This implementation is inspired by your existing projects:

1. **FedSearch-NLP-Federated-RAG-QA-System** - RAG fundamentals
2. **agentic-ai-stock-analysis** - Groq integration patterns
3. **Adaptive-LLM-Based-Conversational-AI** - Memory and context management

## Example: Custom Document Processing

```python
from app import KnowledgeGraphBuilder

builder = KnowledgeGraphBuilder()

# Load your documents
docs = builder.load_documents("./my_documents")

# Build graph
builder.build_knowledge_graph()
builder.setup_vector_store()

# Query examples
queries = [
    "What are the key entities mentioned?",
    "How are company X and person Y related?",
    "Summarize the relationships in the document"
]

for q in queries:
    print(f"Q: {q}")
    print(f"A: {builder.rag_query(q)}\n")
```

## Troubleshooting

### No GROQ_API_KEY Error
```bash
# Make sure .env file exists and has:
GROQ_API_KEY=your_actual_key_here
```

### Ollama Embeddings Not Available
The system falls back to basic retrieval. Install Ollama:
```bash
# Windows: Download from https://ollama.ai
# Then run:
ollama pull nomic-embed-text
ollama serve
```

### JSON Parsing Errors in Entity Extraction
The Groq model sometimes returns non-JSON responses. The code handles this gracefully, but you can improve reliability by:
- Increasing `temperature` for more diverse outputs
- Adding more specific JSON format instructions in prompts
- Using a more capable model if available

## Performance Tips

1. **Reduce document chunk size** for faster processing
2. **Increase `search_kwargs["k"]`** in vector store for more comprehensive retrieval
3. **Use graph caching** for large knowledge graphs
4. **Batch process** multiple documents

## Next Steps

1. ✅ Test with your own documents
2. ✅ Integrate with Neo4j for persistence
3. ✅ Add more entity types for your domain
4. ✅ Create custom relationship extractors
5. ✅ Deploy with FastAPI (like your FedSearch project)

## License

MIT - Inspired by LangChain's RAG patterns and your existing projects

## Resources

- [LangChain Knowledge Graphs](https://www.langchain.com/blog/enhancing-rag-based-applications-accuracy-by-constructing-and-leveraging-knowledge-graphs)
- [Groq API Documentation](https://console.groq.com/docs)
- [PyVis Network Visualization](https://pyvis.readthedocs.io/)
- [NetworkX Graph Library](https://networkx.org/)
