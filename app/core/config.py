from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
    SEMANTIC_YAML_PATH: str = str(PROJECT_ROOT / "semantic" / "all_metrics.yaml")
    CHROMA_COLLECTION_NAME: str = "semantic_metrics"
    DEFAULT_EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    OLLAMA_BASE_URL: str = "http://172.19.144.1:9095"
    PRIMARY_LLM_MODEL: str = "gemma4:31b-cloud"
    FALLBACK_LLM_MODEL: str = "claude-3-5-sonnet-20240620"
    CLAUDE_API_KEY: str = "your-key-here"

settings = Settings()
