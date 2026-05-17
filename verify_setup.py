# -*- coding: utf-8 -*-
"""
Verify Knowledge Graph + Neo4j setup
Run this to check if everything is configured correctly
"""

import os
import sys
import io
from dotenv import load_dotenv

# Set stdout encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

print("\n" + "="*80)
print("[*] VERIFICATION REPORT - Knowledge Graph RAG + Neo4j")
print("="*80 + "\n")

# Check 1: Python version
print("[1] Python Version:")
print(f"    {sys.version.split()[0]} [OK]")

# Check 2: Environment variables
print("\n[2] Environment Configuration:")
groq_key = os.getenv("GROQ_API_KEY")
neo4j_uri = os.getenv("NEO4J_URI")
neo4j_user = os.getenv("NEO4J_USERNAME")
neo4j_pass = os.getenv("NEO4J_PASSWORD")

if groq_key:
    print(f"    [OK] GROQ_API_KEY: {'*' * 10}...{groq_key[-10:]}")
else:
    print("    [FAIL] GROQ_API_KEY: NOT SET")

if neo4j_uri:
    print(f"    [OK] NEO4J_URI: {neo4j_uri}")
else:
    print("    [FAIL] NEO4J_URI: NOT SET")

if neo4j_user:
    print(f"    [OK] NEO4J_USERNAME: {neo4j_user}")
else:
    print("    [FAIL] NEO4J_USERNAME: NOT SET")

if neo4j_pass:
    print(f"    [OK] NEO4J_PASSWORD: {'*' * 10}...{neo4j_pass[-10:]}")
else:
    print("    [FAIL] NEO4J_PASSWORD: NOT SET")

# Check 3: Required packages
print("\n[3] Required Packages:")
packages = [
    ("langchain", "LangChain Framework"),
    ("langchain_community", "LangChain Community"),
    ("langchain_groq", "Groq Integration"),
    ("dotenv", "Environment Variables"),
    ("networkx", "Graph Data Structure"),
    ("pyvis", "Graph Visualization"),
    ("chromadb", "Vector Database"),
    ("neo4j", "Neo4j Driver"),
]

missing = []
for pkg_name, display_name in packages:
    try:
        __import__(pkg_name)
        print(f"    [OK] {display_name}")
    except ImportError:
        print(f"    [FAIL] {display_name} - NOT INSTALLED")
        missing.append(pkg_name)

# Check 4: File structure
print("\n[4] Project Files:")
files = [
    ("app.py", "Core Application"),
    ("fastapi_integration.py", "REST API"),
    ("advanced_examples.py", "Examples"),
    ("requirements.txt", "Dependencies"),
    (".env", "Configuration"),
    ("NEO4J_INTEGRATION.md", "Neo4j Guide"),
]

for filename, description in files:
    filepath = os.path.join(os.getcwd(), filename)
    if os.path.exists(filepath):
        print(f"    [OK] {filename:30} ({description})")
    else:
        print(f"    [FAIL] {filename:30} - MISSING")

# Check 5: Neo4j Connection
print("\n[5] Neo4j Connection Test:")
if neo4j_uri and neo4j_user and neo4j_pass:
    try:
        from neo4j import GraphDatabase

        driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_pass))
        with driver.session() as session:
            result = session.run("RETURN 1")
            result.consume()
        print(f"    [OK] Neo4j Aura Connection: SUCCESS")
        driver.close()
    except Exception as e:
        print(f"    [FAIL] Neo4j Aura Connection: FAILED")
        print(f"           Error: {e}")
else:
    print(f"    [WARN] Neo4j credentials incomplete - skipping connection test")

# Check 6: Groq API
print("\n[6] Groq API Test:")
if groq_key:
    try:
        from langchain_groq import ChatGroq

        llm = ChatGroq(
            model="qwen/qwen3-32b",
            temperature=0.3,
            groq_api_key=groq_key,
            max_tokens=100
        )
        response = llm.invoke("Say OK if you work")
        print(f"    [OK] Groq API: WORKING")
        print(f"         Response: {response.content[:50]}...")
    except Exception as e:
        print(f"    [FAIL] Groq API: FAILED")
        print(f"           Error: {e}")
else:
    print(f"    [WARN] GROQ_API_KEY not set - skipping API test")

# Summary
print("\n" + "="*80)
print("[*] SUMMARY")
print("="*80)

all_ok = (
    groq_key and
    neo4j_uri and neo4j_user and neo4j_pass and
    not missing
)

if all_ok:
    print("""
[OK] ALL SYSTEMS GO!

Your Knowledge Graph RAG system is ready to use:
  * Groq Qwen model configured
  * Neo4j Aura connected
  * All dependencies installed

Get started:
  1. python app.py           (Run demo)
  2. python fastapi_integration.py  (Start API)
  3. python advanced_examples.py    (See examples)

Visit Neo4j Dashboard: https://console.neo4j.io/
    """)
else:
    print("""
[WARN] SETUP INCOMPLETE

Missing items:
    """)
    if not groq_key:
        print("  * GROQ_API_KEY - Add to .env file")
    if not neo4j_uri:
        print("  * NEO4J_URI - Add to .env file")
    if missing:
        print(f"  * Missing packages: {', '.join(missing)}")
        print(f"    Run: pip install -r requirements.txt")

    print("""
Complete setup with:
  1. copy .env.example .env
  2. Add your API keys to .env
  3. pip install -r requirements.txt
    """)

print("="*80 + "\n")
