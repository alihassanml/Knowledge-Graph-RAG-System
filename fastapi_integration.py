"""
FastAPI Integration for Knowledge Graph RAG System
Provides REST API endpoints for knowledge graph construction and querying
Similar pattern to FedSearch-NLP-Federated-RAG-QA-System
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
from pathlib import Path
import tempfile
import logging
from datetime import datetime

from app import KnowledgeGraphBuilder

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Knowledge Graph RAG API",
    description="REST API for building and querying knowledge graphs with Groq Qwen",
    version="1.0.0"
)

# Global knowledge graph builder
knowledge_builders: Dict[str, KnowledgeGraphBuilder] = {}


# ============================================================================
# Pydantic Models
# ============================================================================

class DocumentInput(BaseModel):
    """Document input model"""
    content: str
    source: Optional[str] = None


class QueryRequest(BaseModel):
    """Query request model"""
    query: str
    use_graph: bool = True
    graph_id: str = "default"


class QueryResponse(BaseModel):
    """Query response model"""
    query: str
    answer: str
    context_used: int
    timestamp: str


class GraphStats(BaseModel):
    """Knowledge graph statistics"""
    nodes: int
    edges: int
    entity_types: List[str]
    entities_per_type: Dict[str, int]
    timestamp: str


class ExtractionResult(BaseModel):
    """Entity and relationship extraction result"""
    entities: List[Dict]
    relationships: List[Dict]
    entity_count: int
    relationship_count: int


# ============================================================================
# Utility Functions
# ============================================================================

def get_or_create_builder(graph_id: str = "default") -> KnowledgeGraphBuilder:
    """Get or create a knowledge graph builder"""
    if graph_id not in knowledge_builders:
        knowledge_builders[graph_id] = KnowledgeGraphBuilder()
        logger.info(f"Created new knowledge builder with ID: {graph_id}")
    return knowledge_builders[graph_id]


def cleanup_temp_files(file_path: str):
    """Background task to cleanup temporary files"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Cleaned up temporary file: {file_path}")
    except Exception as e:
        logger.error(f"Error cleaning up file {file_path}: {e}")


# ============================================================================
# Health Check
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Knowledge Graph RAG API",
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# Document Loading & Processing
# ============================================================================

@app.post("/documents/load", response_model=Dict)
async def load_documents(
    file: UploadFile = File(...),
    graph_id: str = "default"
):
    """Load documents from uploaded file"""
    try:
        builder = get_or_create_builder(graph_id)

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        # Load documents
        documents = builder.load_documents(tmp_path)

        return {
            "status": "success",
            "documents_loaded": len(documents),
            "graph_id": graph_id,
            "file_name": file.filename,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error loading documents: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/documents/add", response_model=Dict)
async def add_document(
    doc: DocumentInput,
    graph_id: str = "default"
):
    """Add a single document content"""
    try:
        builder = get_or_create_builder(graph_id)

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".txt") as tmp:
            tmp.write(doc.content)
            tmp_path = tmp.name

        # Load documents
        documents = builder.load_documents(tmp_path)

        return {
            "status": "success",
            "documents_added": len(documents),
            "source": doc.source or "unknown",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error adding document: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Knowledge Graph Building
# ============================================================================

@app.post("/graph/build", response_model=GraphStats)
async def build_graph(graph_id: str = "default"):
    """Build knowledge graph from loaded documents"""
    try:
        builder = get_or_create_builder(graph_id)

        if not builder.documents:
            raise HTTPException(
                status_code=400,
                detail="No documents loaded. Load documents first."
            )

        # Build graph
        builder.build_knowledge_graph()

        # Setup vector store
        builder.setup_vector_store()

        # Calculate statistics
        entity_counts = {}
        for entity_type in builder.entities:
            entity_counts[entity_type] = len(builder.entities[entity_type])

        return GraphStats(
            nodes=builder.graph.number_of_nodes(),
            edges=builder.graph.number_of_edges(),
            entity_types=list(builder.entities.keys()),
            entities_per_type=entity_counts,
            timestamp=datetime.now().isoformat()
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error building graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/graph/stats/{graph_id}", response_model=GraphStats)
async def get_graph_stats(graph_id: str):
    """Get knowledge graph statistics"""
    try:
        if graph_id not in knowledge_builders:
            raise HTTPException(status_code=404, detail="Graph not found")

        builder = knowledge_builders[graph_id]

        entity_counts = {}
        for entity_type in builder.entities:
            entity_counts[entity_type] = len(builder.entities[entity_type])

        return GraphStats(
            nodes=builder.graph.number_of_nodes(),
            edges=builder.graph.number_of_edges(),
            entity_types=list(builder.entities.keys()),
            entities_per_type=entity_counts,
            timestamp=datetime.now().isoformat()
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error getting graph stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Entity & Relationship Extraction
# ============================================================================

@app.post("/extract", response_model=ExtractionResult)
async def extract_entities(
    doc: DocumentInput,
    graph_id: str = "default"
):
    """Extract entities and relationships from text"""
    try:
        builder = get_or_create_builder(graph_id)

        entities, relationships = builder.extract_entities_and_relations(doc.content)

        return ExtractionResult(
            entities=entities,
            relationships=relationships,
            entity_count=len(entities),
            relationship_count=len(relationships)
        )

    except Exception as e:
        logger.error(f"Error extracting entities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Querying & RAG
# ============================================================================

@app.post("/query", response_model=QueryResponse)
async def query_rag(req: QueryRequest):
    """Query knowledge graph using RAG"""
    try:
        builder = get_or_create_builder(req.graph_id)

        if builder.graph.number_of_nodes() == 0:
            raise HTTPException(
                status_code=400,
                detail="Knowledge graph is empty. Build graph first."
            )

        # Perform RAG query
        answer = builder.rag_query(req.query)

        # Get retrieval context count
        context = builder.hybrid_retrieve(req.query, use_graph=req.use_graph)
        context_count = len(context)

        return QueryResponse(
            query=req.query,
            answer=answer,
            context_used=context_count,
            timestamp=datetime.now().isoformat()
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/retrieve")
async def retrieve_context(req: QueryRequest):
    """Retrieve context for a query without generating answer"""
    try:
        builder = get_or_create_builder(req.graph_id)

        context = builder.hybrid_retrieve(req.query, use_graph=req.use_graph)

        return {
            "query": req.query,
            "context": context,
            "context_count": len(context),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error retrieving context: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Graph Visualization & Export
# ============================================================================

@app.get("/graph/visualize/{graph_id}")
async def visualize_graph(graph_id: str, background_tasks: BackgroundTasks):
    """Generate and download graph visualization"""
    try:
        if graph_id not in knowledge_builders:
            raise HTTPException(status_code=404, detail="Graph not found")

        builder = knowledge_builders[graph_id]

        # Create output file
        output_file = f"graph_{graph_id}.html"
        builder.visualize_graph(output_file)

        # Schedule cleanup
        background_tasks.add_task(cleanup_temp_files, output_file)

        return FileResponse(output_file, media_type="text/html")

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error visualizing graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/graph/export/{graph_id}")
async def export_graph(graph_id: str, background_tasks: BackgroundTasks):
    """Export knowledge graph as JSON"""
    try:
        if graph_id not in knowledge_builders:
            raise HTTPException(status_code=404, detail="Graph not found")

        builder = knowledge_builders[graph_id]

        # Save graph
        output_file = f"graph_{graph_id}.json"
        builder.save_graph(output_file)

        # Schedule cleanup
        background_tasks.add_task(cleanup_temp_files, output_file)

        return FileResponse(output_file, media_type="application/json")

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error exporting graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Graph Management
# ============================================================================

@app.get("/graphs")
async def list_graphs():
    """List all available knowledge graphs"""
    return {
        "graphs": list(knowledge_builders.keys()),
        "count": len(knowledge_builders),
        "timestamp": datetime.now().isoformat()
    }


@app.post("/graphs/{graph_id}/clear")
async def clear_graph(graph_id: str):
    """Clear a knowledge graph"""
    try:
        if graph_id in knowledge_builders:
            del knowledge_builders[graph_id]
            return {
                "status": "success",
                "message": f"Graph {graph_id} cleared",
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=404, detail="Graph not found")

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error clearing graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn

    print("\n" + "="*80)
    print("Starting Knowledge Graph RAG API")
    print("="*80)
    print("\nAPI Documentation: http://localhost:8000/docs")
    print("Alternative Docs: http://localhost:8000/redoc")
    print("\n" + "="*80 + "\n")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
