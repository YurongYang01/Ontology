import streamlit as st
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Add project root to path (ensure 'ontology_tool' is importable)
sys.path.append(str(Path(__file__).parent))

from ontology_tool.core.manager import OntologyManager
from ontology_tool.core.importer import DataImporter
from ontology_tool.core.extractor import LLMExtractor
from ontology_tool.core.exporter import RDFExporter
from streamlit_agraph import agraph, Node, Edge, Config

# Initialize components
if 'manager' not in st.session_state:
    st.session_state.manager = OntologyManager(graph_path="memory/ontology/graph.jsonl")

manager = st.session_state.manager
importer = DataImporter(manager)
exporter = RDFExporter(manager)

st.set_page_config(page_title="Ontology Builder", layout="wide")

st.title("🕸️ Ontology Modeling Tool")

# Sidebar for controls
st.sidebar.header("Data Management")

if st.sidebar.button("Clear Graph"):
    manager.clear_graph()
    st.success("Graph cleared!")

# --- Tab 1: Build (Input) ---
tab1, tab2, tab3 = st.tabs(["🏗️ Build", "👀 Visualize", "💾 Export"])

with tab1:
    st.header("Add Data")
    
    # 1. Manual Entry
    with st.expander("Manual Entry"):
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Create Entity")
            e_type = st.text_input("Type (e.g. Person)")
            e_props = st.text_area("Properties (JSON)", "{}")
            if st.button("Add Entity"):
                try:
                    props = json.loads(e_props)
                    manager.create_entity(e_type, props)
                    st.success("Entity added")
                except Exception as e:
                    st.error(f"Error: {e}")

        with col2:
            st.subheader("Create Relation")
            from_id = st.text_input("From ID")
            rel_type = st.text_input("Relation Type")
            to_id = st.text_input("To ID")
            if st.button("Link"):
                manager.create_relation(from_id, rel_type, to_id)
                st.success("Relation added")

    # 2. Unstructured Text (LLM)
    with st.expander("Unstructured Text (AI Extraction)"):
        st.info("Uses DeepSeek-V3 via LangChain")
        text_input = st.text_area("Paste text here...", height=150)
        if st.button("Extract Knowledge"):
            if not os.getenv("DEEPSEEK_API_KEY"):
                st.error("Please set DEEPSEEK_API_KEY in .env")
            else:
                with st.spinner("Analyzing text..."):
                    extractor = LLMExtractor(manager)
                    result = extractor.extract_from_text(text_input)
                    if result:
                        st.success(f"Extracted {len(result.entities)} entities and {len(result.relations)} relations!")
                        st.json(result.dict())

    # 3. Structured Data (CSV)
    with st.expander("Structured Data (CSV Import)"):
        uploaded_file = st.file_uploader("Upload CSV", type="csv")
        if uploaded_file:
            entity_type_csv = st.text_input("Target Entity Type", "Generic")
            if st.button("Import CSV"):
                count = importer.import_csv(uploaded_file, entity_type_csv)
                st.success(f"Imported {count} entities")

# --- Tab 2: Visualize ---
with tab2:
    st.header("Graph Visualization")
    
    entities, relations = manager.load_graph()
    
    if not entities:
        st.warning("Graph is empty. Add data first.")
    else:
        nodes = []
        edges = []
        
        # Convert to agraph format
        for eid, data in entities.items():
            label = data["properties"].get("name", eid)
            nodes.append(Node(id=eid, label=label, size=25, shape="dot"))
            
        for rel in relations:
            edges.append(Edge(source=rel["from"], target=rel["to"], label=rel["rel"]))
            
        config = Config(width=800, height=600, directed=True, nodeHighlightBehavior=True, highlightColor="#F7A7A6")
        
        return_value = agraph(nodes=nodes, edges=edges, config=config)

# --- Tab 3: Export ---
with tab3:
    st.header("Export Ontology")
    
    st.subheader("Statistics")
    stats = manager.get_stats()
    st.write(stats)
    
    st.subheader("Download RDF (Turtle)")
    rdf_data = exporter.export_turtle()
    st.download_button(
        label="Download .ttl",
        data=rdf_data,
        file_name="ontology.ttl",
        mime="text/turtle"
    )

    st.subheader("Raw JSONL")
    with open(manager.graph_path, "r") as f:
        st.download_button("Download JSONL", f, "graph.jsonl")
