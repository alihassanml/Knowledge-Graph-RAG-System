"""
Generate and visualize Knowledge Graph from sample data
This script creates a knowledge graph and generates interactive visualization
"""

from app import KnowledgeGraphBuilder
import json
import os

print("\n" + "="*80)
print("[*] KNOWLEDGE GRAPH GENERATOR")
print("="*80 + "\n")

# Initialize builder
print("[1] Initializing builder...")
builder = KnowledgeGraphBuilder()

# Load documents
print("[2] Loading documents from sample_data/...")
try:
    docs = builder.load_documents("sample_data/")
    print(f"    Loaded {len(docs)} document chunks\n")
except Exception as e:
    print(f"    Error: {e}")
    exit(1)

# Extract entities and build graph manually
print("[3] Building knowledge graph from tech companies...")

# Sample entities and relationships to build a populated graph
sample_entities = [
    ("Steve Jobs", "PERSON"),
    ("Steve Wozniak", "PERSON"),
    ("Ronald Wayne", "PERSON"),
    ("Tim Cook", "PERSON"),
    ("Bill Gates", "PERSON"),
    ("Paul Allen", "PERSON"),
    ("Satya Nadella", "PERSON"),
    ("Larry Page", "PERSON"),
    ("Sergey Brin", "PERSON"),
    ("Sundar Pichai", "PERSON"),
    ("Jeff Bezos", "PERSON"),
    ("Andy Jassy", "PERSON"),
    ("Mark Zuckerberg", "PERSON"),

    ("Apple Inc.", "ORGANIZATION"),
    ("Microsoft", "ORGANIZATION"),
    ("Google", "ORGANIZATION"),
    ("Amazon", "ORGANIZATION"),
    ("Meta Platforms", "ORGANIZATION"),

    ("Los Altos", "LOCATION"),
    ("Cupertino", "LOCATION"),
    ("Seattle", "LOCATION"),
    ("Redmond", "LOCATION"),
    ("Mountain View", "LOCATION"),
    ("Menlo Park", "LOCATION"),
    ("Silicon Valley", "LOCATION"),
    ("California", "LOCATION"),
    ("Washington", "LOCATION"),
]

sample_relationships = [
    ("Steve Jobs", "Apple Inc.", "FOUNDED"),
    ("Steve Wozniak", "Apple Inc.", "FOUNDED"),
    ("Ronald Wayne", "Apple Inc.", "FOUNDED"),
    ("Tim Cook", "Apple Inc.", "CEO"),

    ("Bill Gates", "Microsoft", "FOUNDED"),
    ("Paul Allen", "Microsoft", "FOUNDED"),
    ("Satya Nadella", "Microsoft", "CEO"),

    ("Larry Page", "Google", "FOUNDED"),
    ("Sergey Brin", "Google", "FOUNDED"),
    ("Sundar Pichai", "Google", "CEO"),

    ("Jeff Bezos", "Amazon", "FOUNDED"),
    ("Andy Jassy", "Amazon", "CEO"),

    ("Mark Zuckerberg", "Meta Platforms", "FOUNDED"),
    ("Mark Zuckerberg", "Meta Platforms", "CEO"),

    ("Apple Inc.", "Cupertino", "HEADQUARTERED"),
    ("Apple Inc.", "Silicon Valley", "LOCATED"),
    ("Apple Inc.", "California", "LOCATED"),

    ("Microsoft", "Redmond", "HEADQUARTERED"),
    ("Microsoft", "Washington", "LOCATED"),

    ("Google", "Mountain View", "HEADQUARTERED"),
    ("Google", "Silicon Valley", "LOCATED"),
    ("Google", "California", "LOCATED"),

    ("Amazon", "Seattle", "HEADQUARTERED"),
    ("Amazon", "Washington", "LOCATED"),

    ("Meta Platforms", "Menlo Park", "HEADQUARTERED"),
    ("Meta Platforms", "Silicon Valley", "LOCATED"),
    ("Meta Platforms", "California", "LOCATED"),
]

# Add to graph
print("    Adding entities...")
for entity_name, entity_type in sample_entities:
    builder.graph.add_node(entity_name, type=entity_type)
    builder.entities[entity_type].append(entity_name)

print(f"    Added {len(sample_entities)} entities")

print("    Adding relationships...")
for source, target, relation in sample_relationships:
    builder.graph.add_edge(source, target, relation=relation)
    builder.relationships.append((source, target, relation))

print(f"    Added {len(sample_relationships)} relationships\n")

# Show statistics
print("[4] Graph Statistics:")
print(f"    Total Nodes: {builder.graph.number_of_nodes()}")
print(f"    Total Edges: {builder.graph.number_of_edges()}")
print()

# Save as JSON
print("[5] Saving graph as JSON...")
builder.save_graph("knowledge_graph.json")
print("    Saved to: knowledge_graph.json\n")

# Visualize
print("[6] Generating interactive visualization...")
try:
    builder.visualize_graph("knowledge_graph.html")
    print("    Saved to: knowledge_graph.html")
    print("    [OK] Open in browser: knowledge_graph.html\n")
except Exception as e:
    print(f"    Error: {e}\n")

# Display sample data
print("[7] Sample Graph Data:")
print()
print("    ENTITIES BY TYPE:")
for entity_type, entities in builder.entities.items():
    print(f"      {entity_type}: {len(entities)}")
    for entity in list(entities)[:3]:
        print(f"        - {entity}")
    if len(entities) > 3:
        print(f"        ... and {len(entities)-3} more")

print()
print("    SAMPLE RELATIONSHIPS:")
for source, target, relation in builder.relationships[:5]:
    print(f"      {source} --[{relation}]--> {target}")
if len(builder.relationships) > 5:
    print(f"      ... and {len(builder.relationships)-5} more")

print()
print("="*80)
print("[OK] GRAPH GENERATION COMPLETE!")
print("="*80)
print()
print("FILES CREATED:")
print("  1. knowledge_graph.json   - Graph data as JSON")
print("  2. knowledge_graph.html   - Interactive visualization")
print()
print("HOW TO VIEW:")
print("  1. JSON:  Open knowledge_graph.json in text editor")
print("  2. HTML:  Open knowledge_graph.html in web browser")
print()
print("NEXT STEPS:")
print("  1. Open knowledge_graph.html in your web browser")
print("  2. Drag nodes to explore relationships")
print("  3. Click nodes to see entity details")
print()
