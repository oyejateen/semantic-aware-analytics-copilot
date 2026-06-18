import requests
import json
from typing import Optional, List
from app.core.config import settings
from app.models.semantic import AmbiguousTerm, ContextPacket

class LLMService:
    def __init__(self):
        self.ollama_url = f"{settings.OLLAMA_BASE_URL}/api/generate"
        self.primary_model = settings.PRIMARY_LLM_MODEL
        self.fallback_model = settings.FALLBACK_LLM_MODEL

    def _call_ollama(self, prompt: str) -> Optional[str]:
        """Internal helper to call Ollama API."""
        try:
            payload = {
                "model": self.primary_model,
                "prompt": prompt,
                "stream": False,
                "format": "json" if "json" in prompt.lower() else None
            }
            response = requests.post(self.ollama_url, json=payload, timeout=120)
            response.raise_for_status()
            return response.json().get("response")
        except Exception as e:
            print(f"Ollama Error: {e}")
            return None

    def _call_claude(self, prompt: str) -> Optional[str]:
        """Fallback to Claude API."""
        # In a real implementation, use the anthropic SDK
        # For now, we'll simulate the fallback logic
        print("Routing to Claude Fallback...")
        return f"Claude Generated Response for: {prompt[:50]}..."

    def detect_ambiguity(self, query: str, ambiguous_terms: List[AmbiguousTerm]) -> Optional[AmbiguousTerm]:
        """
        Checks if the query contains any terms that are marked as ambiguous.
        Returns the AmbiguousTerm object if found, otherwise None.
        """
        # First, a simple keyword check for speed
        for term_obj in ambiguous_terms:
            if term_obj.term.lower() in query.lower():
                return term_obj

        # Second, use the LLM to detect semantic ambiguity and handle misspellings
        term_list = [t.term for t in ambiguous_terms]
        prompt = f"""
        Analyze the following user query: "{query}"
        Known ambiguous business terms: {term_list}

        Is the user asking about any of these terms, even if they are misspelled or phrased vaguely?
        If the query is semantically referring to any of these terms, return JSON: {{"ambiguous": true, "term": "the_matched_term_from_the_list"}}
        If no ambiguous term is being referred to, return JSON: {{"ambiguous": false}}

        Crucial: Map the user's misspelled or vague term back to the EXACT term from the provided list.
        """
        response = self._call_ollama(prompt)
        if not response:
            response = self._call_claude(prompt)

        if response:
            try:
                res_json = json.loads(response)
                if res_json.get("ambiguous"):
                    term_name = res_json.get("term")
                    return next((t for t in ambiguous_terms if t.term == term_name), None)
            except Exception:
                pass

        return None

    def generate_sql(self, packet: ContextPacket) -> str:
        """
        Generates SQL based on the Context Packet.
        """
        prompt = f"""
        You are an expert SQL generator for the Airbnb NYC dataset.

        User Question: {packet.question}

        Relevant Semantic Context:
        - Metrics: {packet.retrieved_metrics}
        - Join Paths: {packet.join_paths}
        - Caveats: {packet.business_caveats}

        Generate a valid SQL query. Return ONLY the SQL.
        """
        sql = self._call_ollama(prompt)
        if not sql:
            sql = self._call_claude(prompt)

        return sql
