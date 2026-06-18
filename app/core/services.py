from app.core.config import settings
from app.services.semantic_service import SemanticService
from app.services.rag_service import RAGService
from app.services.llm_service import LLMService

class ServiceContainer:
    def __init__(self):
        self.semantic_service: SemanticService = None
        self.rag_service: RAGService = None
        self.llm_service: LLMService = None

    def init_services(self):
        try:
            self.semantic_service = SemanticService(yaml_path=settings.SEMANTIC_YAML_PATH)
            self.rag_service = RAGService(
                collection_name=settings.CHROMA_COLLECTION_NAME,
                embedding_model=settings.DEFAULT_EMBEDDING_MODEL
            )
            self.llm_service = LLMService()

            # Index both metrics AND ambiguous terms for high-concurrency retrieval
            self.rag_service.index_metrics(
                self.semantic_service.get_metrics(),
                self.semantic_service.get_ambiguous_terms()
            )
        except Exception as e:
            print(f"Error initializing services: {e}")

services = ServiceContainer()
