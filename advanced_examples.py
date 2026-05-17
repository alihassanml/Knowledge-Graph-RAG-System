"""
Advanced Examples for Knowledge Graph RAG System
Demonstrates advanced use cases and patterns
"""

from app import KnowledgeGraphBuilder
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_1_research_papers():
    """Extract knowledge graphs from research papers"""
    builder = KnowledgeGraphBuilder()

    paper_text = """
    In their seminal work, Hinton et al. (2006) demonstrated that deep neural networks
    could be pre-trained using restricted Boltzmann machines. This breakthrough was developed
    at the University of Toronto and later adopted by companies like Google and OpenAI.

    The technique enabled faster convergence on complex datasets. Bengio, another researcher
    at University of Toronto, further contributed to deep learning theory. Their combined
    work at the Neural Information Processing Systems (NIPS) conference shaped the field
    of artificial intelligence significantly.
    """

    # Extract entities and relationships
    entities, relations = builder.extract_entities_and_relations(paper_text)

    print("\n" + "="*80)
    print("EXAMPLE 1: Research Paper Knowledge Extraction")
    print("="*80)
    print("\nExtracted Entities:")
    for entity in entities:
        print(f"  - {entity.get('text')} ({entity.get('type')})")

    print("\nExtracted Relationships:")
    for rel in relations:
        print(f"  - {rel.get('source')} --[{rel.get('relation')}]--> {rel.get('target')}")


def example_2_multi_document_analysis():
    """Build knowledge graph from multiple documents"""
    builder = KnowledgeGraphBuilder()

    documents = [
        """
        Steve Jobs co-founded Apple Computer Company in Los Altos, California in 1976
        along with Steve Wozniak. They later hired John Sculley as CEO. Apple went public
        in 1980 in San Francisco.
        """,
        """
        Bill Gates and Paul Allen founded Microsoft in Seattle, Washington in 1975.
        They developed MS-DOS for IBM. Satya Nadella is the current CEO of Microsoft
        since 2014.
        """,
        """
        Google was founded by Larry Page and Sergey Brin at Stanford University in 1998.
        They developed the PageRank algorithm. Google went public in 2004 in New York.
        Sundar Pichai became CEO in 2015.
        """
    ]

    print("\n" + "="*80)
    print("EXAMPLE 2: Multi-Document Knowledge Graph")
    print("="*80)

    for i, doc in enumerate(documents, 1):
        print(f"\nProcessing Document {i}...")
        entities, relations = builder.extract_entities_and_relations(doc)

        # Add to graph
        for entity in entities:
            builder.graph.add_node(
                entity.get("text"),
                type=entity.get("type")
            )

        for rel in relations:
            builder.graph.add_edge(
                rel.get("source"),
                rel.get("target"),
                relation=rel.get("relation")
            )

    print(f"\nGraph Statistics:")
    print(f"  Total Nodes: {builder.graph.number_of_nodes()}")
    print(f"  Total Edges: {builder.graph.number_of_edges()}")
    print(f"\nNode List: {list(builder.graph.nodes())}")


def example_3_entity_relationship_analysis():
    """Analyze entity relationships and connections"""
    builder = KnowledgeGraphBuilder()

    text = """
    Tim Cook is the CEO of Apple. Apple acquired Beats Electronics, which was founded
    by Dr. Dre and Jimmy Iovine. Jimmy Iovine worked with Eminem at Aftermath Entertainment
    in Los Angeles. Eminem is a rapper from Detroit, Michigan.
    """

    entities, relations = builder.extract_entities_and_relations(text)

    print("\n" + "="*80)
    print("EXAMPLE 3: Entity Relationship Analysis")
    print("="*80)

    # Build graph
    for entity in entities:
        builder.graph.add_node(entity.get("text"), type=entity.get("type"))

    for rel in relations:
        builder.graph.add_edge(rel.get("source"), rel.get("target"))

    # Analyze connections
    print("\nEntity Connection Analysis:")
    for node in builder.graph.nodes():
        predecessors = list(builder.graph.predecessors(node))
        successors = list(builder.graph.successors(node))

        if predecessors or successors:
            print(f"\n  {node}:")
            if predecessors:
                print(f"    ← Connected from: {predecessors}")
            if successors:
                print(f"    → Connected to: {successors}")


def example_4_concept_extraction():
    """Extract key concepts and their relationships"""
    builder = KnowledgeGraphBuilder()

    business_text = """
    Cloud Computing has transformed how organizations manage infrastructure.
    Amazon Web Services (AWS) pioneered cloud services and competes with
    Microsoft Azure and Google Cloud Platform.

    Machine Learning is a subset of Artificial Intelligence that powers recommendation systems.
    Deep Learning, a subset of Machine Learning, uses neural networks.
    Natural Language Processing enables computers to understand human language.
    """

    entities, relations = builder.extract_entities_and_relations(business_text)

    print("\n" + "="*80)
    print("EXAMPLE 4: Concept Extraction and Classification")
    print("="*80)

    # Organize by type
    by_type = {}
    for entity in entities:
        entity_type = entity.get("type", "UNKNOWN")
        if entity_type not in by_type:
            by_type[entity_type] = []
        by_type[entity_type].append(entity.get("text"))

    print("\nConcepts by Type:")
    for entity_type, items in by_type.items():
        print(f"\n  {entity_type}:")
        for item in items:
            print(f"    - {item}")


def example_5_graph_visualization_config():
    """Advanced graph visualization configuration"""
    builder = KnowledgeGraphBuilder()

    # Add sample data
    builder.graph.add_node("Alice", type="PERSON", department="Engineering")
    builder.graph.add_node("Bob", type="PERSON", department="Sales")
    builder.graph.add_node("TechCorp", type="ORGANIZATION", industry="Technology")

    builder.graph.add_edge("Alice", "TechCorp", relation="works_at")
    builder.graph.add_edge("Bob", "TechCorp", relation="works_at")
    builder.graph.add_edge("Alice", "Bob", relation="knows")

    print("\n" + "="*80)
    print("EXAMPLE 5: Advanced Graph Visualization")
    print("="*80)

    # Save as JSON with metadata
    graph_data = {
        "nodes": [
            {"id": node, **attrs}
            for node, attrs in builder.graph.nodes(data=True)
        ],
        "edges": [
            {"source": source, "target": target, **attrs}
            for source, target, attrs in builder.graph.edges(data=True)
        ],
        "metadata": {
            "created": "2024",
            "type": "organizational_network",
            "total_nodes": builder.graph.number_of_nodes(),
            "total_edges": builder.graph.number_of_edges()
        }
    }

    # Save to file
    with open("example_graph.json", "w") as f:
        json.dump(graph_data, f, indent=2)

    print(f"\nGraph saved with {len(graph_data['nodes'])} nodes and {len(graph_data['edges'])} edges")
    print("Saved to: example_graph.json")


def example_6_rag_with_context_aggregation():
    """Demonstrate RAG with aggregated context from multiple sources"""
    builder = KnowledgeGraphBuilder()

    # Simulate loaded documents
    builder.documents = [
        type('Doc', (), {
            'page_content': "Apple Inc. is a technology company founded in 1976.",
            'metadata': {'source': 'doc1'}
        })(),
        type('Doc', (), {
            'page_content': "Tim Cook became CEO of Apple in 2011.",
            'metadata': {'source': 'doc2'}
        })(),
        type('Doc', (), {
            'page_content': "Apple released the iPhone in 2007, changing mobile computing.",
            'metadata': {'source': 'doc3'}
        })(),
    ]

    print("\n" + "="*80)
    print("EXAMPLE 6: RAG Context Aggregation")
    print("="*80)

    query = "Tell me about Apple's history and leadership"
    print(f"\nQuery: {query}")

    # Simulate retrieval
    context_items = [
        "Apple Inc. is a technology company founded in 1976.",
        "Tim Cook became CEO of Apple in 2011.",
        "Apple released the iPhone in 2007, changing mobile computing."
    ]

    aggregated_context = "\n\n".join(context_items)
    print(f"\nAggregated Context:")
    print("-" * 40)
    print(aggregated_context)
    print("-" * 40)


def example_7_export_formats():
    """Export knowledge graph in multiple formats"""
    builder = KnowledgeGraphBuilder()

    # Add sample data
    builder.graph.add_node("Python", type="CONCEPT")
    builder.graph.add_node("Machine Learning", type="CONCEPT")
    builder.graph.add_node("Data Science", type="CONCEPT")

    builder.graph.add_edge("Python", "Machine Learning", relation="used_in")
    builder.graph.add_edge("Machine Learning", "Data Science", relation="subset_of")

    print("\n" + "="*80)
    print("EXAMPLE 7: Knowledge Graph Export Formats")
    print("="*80)

    # Export as JSON
    graph_json = {
        "nodes": [{"id": n, **attrs} for n, attrs in builder.graph.nodes(data=True)],
        "edges": [{"s": s, "t": t, **attrs} for s, t, attrs in builder.graph.edges(data=True)]
    }

    print("\n1. JSON Format:")
    print(json.dumps(graph_json, indent=2)[:200] + "...")

    # Export as adjacency list
    print("\n2. Adjacency List Format:")
    for node in builder.graph.nodes():
        neighbors = list(builder.graph.neighbors(node))
        print(f"  {node}: {neighbors}")

    # Export statistics
    print("\n3. Graph Statistics:")
    stats = {
        "total_nodes": builder.graph.number_of_nodes(),
        "total_edges": builder.graph.number_of_edges(),
        "node_types": list(set(attrs.get("type") for _, attrs in builder.graph.nodes(data=True))),
        "density": builder.graph.number_of_edges() / (builder.graph.number_of_nodes() ** 2) if builder.graph.number_of_nodes() > 0 else 0
    }
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    print("\n🔥 Running Advanced Knowledge Graph Examples\n")

    try:
        example_1_research_papers()
    except Exception as e:
        logger.error(f"Example 1 error: {e}")

    try:
        example_2_multi_document_analysis()
    except Exception as e:
        logger.error(f"Example 2 error: {e}")

    try:
        example_3_entity_relationship_analysis()
    except Exception as e:
        logger.error(f"Example 3 error: {e}")

    try:
        example_4_concept_extraction()
    except Exception as e:
        logger.error(f"Example 4 error: {e}")

    try:
        example_5_graph_visualization_config()
    except Exception as e:
        logger.error(f"Example 5 error: {e}")

    try:
        example_6_rag_with_context_aggregation()
    except Exception as e:
        logger.error(f"Example 6 error: {e}")

    try:
        example_7_export_formats()
    except Exception as e:
        logger.error(f"Example 7 error: {e}")

    print("\n✅ All examples completed!")
