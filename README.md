# Kona (코나)

Semantic-aware analytical copilot for contextual data analysis. Kona transforms natural language questions into precise SQL by leveraging a semantic layer and vector-based retrieval.

## 🚀 Quick Start

### 1. Setup
```bash
# Install dependencies
uv sync
```

### 2. Run Backend
```bash
# Start the FastAPI server
uvicorn app.main:app --reload --port 8000
```

### 3. Run Frontend
```bash
# Start the Streamlit interface
streamlit run frontend/app.py
```

---

## 🛠 How it Works

### 🧠 Embeddings & Indexing
On startup, Kona reads the `semantic/all_metrics.yaml` and indexes all **Metric Definitions** and **Ambiguous Terms** into **ChromaDB**. It converts textual descriptions into vector embeddings, allowing the system to find the right metrics even if the user's phrasing doesn't match exactly.

### 🔍 Semantic Search & Ambiguity
1. **Vector Retrieval**: The system uses cosine similarity to find metrics related to the user's query.
2. **Strict Ambiguity Check**:
   - **RAG-First**: It first checks if the query's vector is close to a known "Ambiguous Term".
   - **LLM Fallback**: If RAG is inconclusive, an LLM analyzes the query for semantic vagueness or misspellings.
3. **Clarification**: If ambiguity is detected, the UI prompts the user to select the correct business meaning before generating SQL.

### 💻 SQL Generation
Once the context is disambiguated, a **Context Packet** (Question + Retrieved Metrics + Join Paths + Business Caveats) is sent to the LLM to generate valid, execution-ready SQL.

## 📂 Project Structure
- `app/api/`: FastAPI endpoints.
- `app/core/`: Service orchestration and configuration.
- `app/services/`: Logic for RAG, LLM, and Semantic Layer.
- `app/models/`: Pydantic schemas for data validation.
- `frontend/`: Streamlit user interface.
- `semantic_layer.yaml`: The source of truth for business metrics.
