"""
Knowledge Graph Construction and RAG System using Groq Qwen Model
Hybrid retrieval combining vector search, keyword search, and graph traversal
Enhanced with Neo4j integration for persistent storage
"""

import os
from typing import List, Optional, Tuple, Dict
from dotenv import load_dotenv
import logging
from neo4j import GraphDatabase

# LangChain imports
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.documents import Document

# Groq imports
from langchain_groq import ChatGroq

# Graph imports
from pyvis.network import Network
import networkx as nx
from collections import defaultdict
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


class KnowledgeGraphBuilder:
    """Build and manage knowledge graphs for RAG applications with Neo4j persistence"""

    def __init__(self, groq_api_key: Optional[str] = None, use_neo4j: bool = True):
        """Initialize the knowledge graph builder with Groq Qwen model and Neo4j backend"""
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")

        # Neo4j configuration
        self.use_neo4j = use_neo4j
        self.neo4j_driver = None
        self.neo4j_session = None

        if use_neo4j:
            self._init_neo4j()

        # Initialize Groq LLM
        self.llm = ChatGroq(
            model="qwen/qwen3-32b",
            temperature=0.3,
            groq_api_key=self.groq_api_key,
            max_tokens=2048
        )

        # Graph storage
        self.graph = nx.MultiDiGraph()
        self.entities = defaultdict(list)
        self.relationships = []
        self.documents = []

        # Vector store
        self.vector_store = None
        self.retriever = None

        logger.info("Knowledge Graph Builder initialized with Groq Qwen + Neo4j")

    def _init_neo4j(self):
        """Initialize Neo4j connection"""
        try:
            uri = os.getenv("NEO4J_URI")
            username = os.getenv("NEO4J_USERNAME")
            password = os.getenv("NEO4J_PASSWORD")

            if not all([uri, username, password]):
                logger.warning("Neo4j credentials not found. Using in-memory graph only.")
                self.use_neo4j = False
                return

            self.neo4j_driver = GraphDatabase.driver(uri, auth=(username, password))
            logger.info("✅ Connected to Neo4j Aura")

        except Exception as e:
            logger.warning(f"Neo4j connection failed: {e}. Using in-memory graph.")
            self.use_neo4j = False

    def _execute_neo4j_query(self, query: str, params: Dict = None) -> List[Dict]:
        """Execute Neo4j Cypher query"""
        if not self.use_neo4j or not self.neo4j_driver:
            return []

        try:
            with self.neo4j_driver.session() as session:
                result = session.run(query, params or {})
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Neo4j query error: {e}")
            return []

    def _add_entity_to_neo4j(self, entity_name: str, entity_type: str, doc_id: str):
        """Add entity node to Neo4j"""
        if not self.use_neo4j:
            return

        query = """
        MERGE (e:Entity {name: $name})
        SET e.type = $type, e.doc_id = $doc_id
        RETURN e
        """
        self._execute_neo4j_query(query, {
            "name": entity_name,
            "type": entity_type,
            "doc_id": doc_id
        })

    def _add_relationship_to_neo4j(self, source: str, target: str, relation: str):
        """Add relationship to Neo4j"""
        if not self.use_neo4j:
            return

        query = """
        MATCH (s:Entity {name: $source}), (t:Entity {name: $target})
        CREATE (s)-[r:RELATES {type: $relation}]->(t)
        RETURN r
        """
        self._execute_neo4j_query(query, {
            "source": source,
            "target": target,
            "relation": relation
        })

    def load_documents(self, source: str) -> List[Document]:
        """Load documents from file or directory"""
        try:
            documents = []

            if os.path.isfile(source):
                # Load single file
                with open(source, 'r', encoding='utf-8') as f:
                    content = f.read()
                documents.append(Document(page_content=content, metadata={"source": source}))

            elif os.path.isdir(source):
                # Load all .txt files from directory
                for root, dirs, files in os.walk(source):
                    for file in files:
                        if file.endswith('.txt'):
                            filepath = os.path.join(root, file)
                            with open(filepath, 'r', encoding='utf-8') as f:
                                content = f.read()
                            documents.append(Document(page_content=content, metadata={"source": filepath}))
            else:
                raise FileNotFoundError(f"Source {source} not found")

            if not documents:
                raise ValueError("No documents found")

            # Split documents into chunks
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
            )
            self.documents = splitter.split_documents(documents)
            logger.info(f"Loaded {len(self.documents)} document chunks from {len(documents)} file(s)")
            return self.documents

        except Exception as e:
            logger.error(f"Error loading documents: {e}")
            raise

    def extract_entities_and_relations(self, text: str) -> Tuple[List[dict], List[dict]]:
        """
        Extract entities and relationships using Groq Qwen model
        Returns entities and their relationships
        """
        prompt = f"""Extract entities and relationships from text. Return ONLY valid JSON, no extra text.

Text: {text[:1000]}

Return exactly this JSON format:
{{"entities": [{{"text": "name", "type": "PERSON"}}], "relationships": [{{"source": "name1", "target": "name2", "relation": "type"}}]}}"""

        try:
            response = self.llm.invoke(prompt)
            content = response.content.strip()

            # Extract JSON more carefully
            import re
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                try:
                    result = json.loads(json_match.group())
                    entities = result.get("entities", [])
                    relations = result.get("relationships", [])
                    return entities if isinstance(entities, list) else [], relations if isinstance(relations, list) else []
                except json.JSONDecodeError:
                    logger.debug(f"JSON parse failed on: {json_match.group()[:100]}")
                    return [], []
            return [], []

        except Exception as e:
            logger.debug(f"Entity extraction error: {e}")
            return [], []

    def build_knowledge_graph(self) -> nx.MultiDiGraph:
        """Build knowledge graph from documents in both NetworkX and Neo4j"""
        logger.info("Building knowledge graph...")

        for i, doc in enumerate(self.documents):
            logger.info(f"Processing document {i+1}/{len(self.documents)}")

            entities, relationships = self.extract_entities_and_relations(doc.page_content)
            doc_id = doc.metadata.get("source", "unknown")

            # Add entities
            for entity in entities:
                entity_name = entity.get("text", "")
                entity_type = entity.get("type", "UNKNOWN")

                # Add to NetworkX
                self.graph.add_node(entity_name, type=entity_type, doc_id=doc_id)
                self.entities[entity_type].append(entity_name)

                # Add to Neo4j
                self._add_entity_to_neo4j(entity_name, entity_type, doc_id)

            # Add relationships
            for rel in relationships:
                source = rel.get("source", "")
                target = rel.get("target", "")
                relation = rel.get("relation", "RELATED_TO")

                if source and target:
                    self.graph.add_edge(source, target, relation=relation)
                    self.relationships.append((source, target, relation))
                    self._add_relationship_to_neo4j(source, target, relation)

        logger.info(f"Graph built: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges")
        if self.use_neo4j:
            logger.info("✅ Graph persisted in Neo4j")
        return self.graph

    def query_neo4j_graph(self) -> List[Dict]:
        """Query Neo4j knowledge graph with Cypher"""
        if not self.use_neo4j:
            logger.warning("Neo4j not available")
            return []

        cypher = """
        MATCH (e:Entity)-[r]->(t)
        RETURN e.name as entity, r.type as relationship, t.name as target
        LIMIT 10
        """
        return self._execute_neo4j_query(cypher)

    def get_neo4j_stats(self) -> Dict:
        """Get Neo4j graph statistics"""
        if not self.use_neo4j:
            return {}

        stats = {}
        # Get node count
        nodes = self._execute_neo4j_query("MATCH (n:Entity) RETURN count(n) as count")
        stats["neo4j_nodes"] = nodes[0]["count"] if nodes else 0

        # Get relationship count
        rels = self._execute_neo4j_query("MATCH ()-[r:RELATES]->() RETURN count(r) as count")
        stats["neo4j_relationships"] = rels[0]["count"] if rels else 0

        return stats

    def setup_vector_store(self, documents: Optional[List[Document]] = None):
        """Setup vector store for hybrid retrieval"""
        if documents is None:
            documents = self.documents

        logger.info("Setting up vector store...")

        try:
            # Using Ollama embeddings (runs locally)
            embeddings = OllamaEmbeddings(model="nomic-embed-text")

            self.vector_store = Chroma.from_documents(
                documents=documents,
                embedding=embeddings,
                collection_name="knowledge_graph"
            )
            self.retriever = self.vector_store.as_retriever(
                search_kwargs={"k": 3}
            )
            logger.info("Vector store initialized successfully")

        except Exception as e:
            logger.warning(f"Ollama embeddings not available: {e}")
            logger.info("Falling back to basic retrieval")

    def hybrid_retrieve(self, query: str, use_graph: bool = True) -> List[str]:
        """
        Hybrid retrieval combining:
        1. Vector search (semantic similarity)
        2. Keyword matching
        3. Graph traversal (entity relationships)
        """
        results = []

        # 1. Vector search
        if self.retriever:
            try:
                vector_results = self.retriever.invoke(query)
                results.extend([doc.page_content for doc in vector_results])
                logger.info(f"Vector search returned {len(vector_results)} results")
            except Exception as e:
                logger.warning(f"Vector search failed: {e}")

        # 2. Keyword search
        keywords = query.lower().split()
        keyword_matches = []
        for doc in self.documents:
            if any(keyword in doc.page_content.lower() for keyword in keywords):
                keyword_matches.append(doc.page_content)
        results.extend(keyword_matches[:3])
        logger.info(f"Keyword search returned {len(keyword_matches[:3])} results")

        # 3. Graph traversal - find related entities
        if use_graph and self.graph.number_of_nodes() > 0:
            query_entities = self.extract_entities_and_relations(query)[0]
            graph_results = []

            for entity in query_entities:
                entity_name = entity.get("text", "")
                if entity_name in self.graph:
                    neighbors = list(self.graph.neighbors(entity_name))
                    graph_results.extend(neighbors[:3])

            logger.info(f"Graph traversal found {len(set(graph_results))} related entities")
            results.extend(list(set(graph_results)))

        return list(set(results))[:5]

    def rag_query(self, query: str) -> str:
        """
        Perform RAG (Retrieval-Augmented Generation) using hybrid retrieval
        """
        logger.info(f"Processing RAG query: {query}")

        # Retrieve relevant context
        context_items = self.hybrid_retrieve(query)
        context = "\n\n".join(context_items)

        # Generate answer using Groq Qwen
        rag_prompt = f"""
        You are a helpful assistant answering questions based on the following context.

        CONTEXT:
        {context}

        QUESTION: {query}

        Provide a comprehensive answer based on the context. If the context doesn't contain relevant information, say so.
        """

        try:
            response = self.llm.invoke(rag_prompt)
            answer = response.content
            logger.info("RAG query completed successfully")
            return answer

        except Exception as e:
            logger.error(f"Error in RAG query: {e}")
            return f"Error processing query: {e}"

    def visualize_graph(self, output_file: str = "knowledge_graph.html"):
        """Visualize knowledge graph as interactive HTML"""
        logger.info(f"Visualizing graph to {output_file}")

        try:
            if self.graph.number_of_nodes() == 0:
                logger.warning("Graph is empty - no visualization created")
                return

            net = Network(
                directed=True,
                notebook=False,
                height="750px",
                width="100%"
            )

            # Add nodes with colors based on entity type
            color_map = {
                "PERSON": "#FF6B6B",
                "ORGANIZATION": "#4ECDC4",
                "LOCATION": "#45B7D1",
                "CONCEPT": "#FFA07A",
                "UNKNOWN": "#95E1D3"
            }

            for node, attrs in self.graph.nodes(data=True):
                entity_type = attrs.get("type", "UNKNOWN")
                color = color_map.get(entity_type, "#95E1D3")
                net.add_node(node, label=node, color=color, title=entity_type)

            # Add edges
            for source, target, attrs in self.graph.edges(data=True):
                relation = attrs.get("relation", "RELATED_TO")
                net.add_edge(source, target, title=relation)

            net.show(output_file)
            logger.info(f"Graph visualization saved to {output_file}")

        except Exception as e:
            logger.error(f"Error visualizing graph: {e}")

    def save_graph(self, filepath: str = "knowledge_graph.json"):
        """Save knowledge graph as JSON"""
        try:
            graph_data = {
                "nodes": [
                    {"id": node, **attrs}
                    for node, attrs in self.graph.nodes(data=True)
                ],
                "edges": [
                    {"source": source, "target": target, **attrs}
                    for source, target, attrs in self.graph.edges(data=True)
                ],
                "entities": {k: v for k, v in self.entities.items()},
                "statistics": {
                    "nodes": self.graph.number_of_nodes(),
                    "edges": self.graph.number_of_edges(),
                    "entity_types": list(self.entities.keys())
                }
            }

            with open(filepath, "w") as f:
                json.dump(graph_data, f, indent=2)

            logger.info(f"Knowledge graph saved to {filepath}")

        except Exception as e:
            logger.error(f"Error saving graph: {e}")

    def close(self):
        """Close Neo4j connection"""
        if self.neo4j_driver:
            self.neo4j_driver.close()
            logger.info("Neo4j connection closed")

    def __del__(self):
        """Destructor to ensure Neo4j connection is closed"""
        self.close()


def main():
    """Main function demonstrating knowledge graph building and RAG"""

    # Initialize builder
    builder = KnowledgeGraphBuilder()

    # Example: Create sample data
    sample_data_dir = "sample_data"
    os.makedirs(sample_data_dir, exist_ok=True)

    # Create sample documents if they don't exist
    sample_doc = os.path.join(sample_data_dir, "sample.txt")
    if not os.path.exists(sample_doc):
        with open(sample_doc, "w") as f:
            f.write("""
            Apple Inc. is a technology company founded by Steve Jobs in 1976 in Los Altos, California.
            The company developed the iPhone, which became one of the most successful products ever.
            Tim Cook is the current CEO of Apple. Apple has offices in Cupertino and around the world.

            Microsoft was founded by Bill Gates and Paul Allen in 1975 in Seattle, Washington.
            Satya Nadella is the current CEO of Microsoft. Microsoft develops Windows and Azure.

            Google was founded by Larry Page and Sergey Brin in 1998 in Mountain View, California.
            Sundar Pichai is the current CEO of Google. Google develops Android and Chrome.
            """)

    # Load documents
    documents = builder.load_documents(sample_data_dir)

    # Build knowledge graph
    builder.build_knowledge_graph()

    # Setup vector store
    builder.setup_vector_store()

    # Visualize graph
    builder.visualize_graph()

    # Save graph
    builder.save_graph()

    # Test RAG queries
    test_queries = [
        "Who founded Apple and where?",
        "What is the relationship between Microsoft and Bill Gates?",
        "List major tech companies and their CEOs",
        "Which companies have operations in California?"
    ]

    print("\n" + "="*80)
    print("[*] KNOWLEDGE GRAPH RAG SYSTEM - GROQ QWEN + NEO4J")
    print("="*80 + "\n")

    # Show Neo4j stats
    if builder.use_neo4j:
        stats = builder.get_neo4j_stats()
        print("[OK] Neo4j Connected!")
        print(f"     Nodes in Neo4j: {stats.get('neo4j_nodes', 0)}")
        print(f"     Relationships in Neo4j: {stats.get('neo4j_relationships', 0)}\n")

        # Query Neo4j
        neo4j_results = builder.query_neo4j_graph()
        if neo4j_results:
            print("Sample Neo4j Graph Relationships:")
            for result in neo4j_results[:3]:
                print(f"     {result}\n")
    else:
        print("[WARN] Neo4j not available - using in-memory graph only\n")

    # RAG queries
    print("-" * 80)
    print("RAG QUERIES:\n")
    for query in test_queries:
        print(f"Q: {query}")
        answer = builder.rag_query(query)
        print(f"A: {answer}\n")
        print("-" * 80 + "\n")

    # Cleanup
    builder.close()


if __name__ == "__main__":
    main()