import chromadb
from chromadb.utils import embedding_functions
from typing import List, Optional
from app.models.semantic import MetricDefinition

class RAGService:
    def __init__(self, collection_name: str = "semantic_metrics", embedding_model: str = "all-MiniLM-L6-v2"):
        self.client = chromadb.Client()

        # Setup Embedding Function
        # If 'all-MiniLM-L6-v2' is used, we use the default Chroma embedding function
        # In a real prod setup, we'd add a switch for Ollama nomic-embed-text here
        self.emb_fn = embedding_functions.DefaultEmbeddingFunction()

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.emb_fn
        )

    def index_metrics(self, metrics: List[MetricDefinition], ambiguous_terms: List = None):
        """
        Indexes metric definitions and ambiguous terms into ChromaDB.
        """
        documents = []
        metadatas = []
        ids = []

        # Index Metrics
        for metric in metrics:
            content = f"Metric: {metric.label}. Description: {metric.description}"
            documents.append(content)
            metadatas.append({
                "name": metric.name,
                "type": "metric",
                "certified": metric.certified,
                "owner": metric.owner,
                "grain": metric.grain
            })
            ids.append(metric.name)

        # Index Ambiguous Terms
        if ambiguous_terms:
            for term in ambiguous_terms:
                content = f"Ambiguous Term: {term.term}. Clarification: {term.clarification}"
                documents.append(content)
                metadatas.append({
                    "name": term.term,
                    "type": "ambiguity",
                    "clarification": term.clarification
                })
                ids.append(f"ambig_{term.term}")

        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def retrieve_metrics(self, query: str, n_results: int = 3) -> List[str]:
        """
        Searches for the most relevant metrics.
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results['ids'][0] if results['ids'] else []

    def check_ambiguity(self, query: str, n_results: int = 1) -> Optional[str]:
        """
        Checks if the query is semantically close to any known ambiguous terms.
        Returns the term name if an 'ambiguity' type object is the top match.
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )

        if not results['ids'] or not results['ids'][0]:
            return None

        top_meta = results['metadatas'][0][0]

        if top_meta.get("type") == "ambiguity":
            return top_meta.get("name")

        return None
