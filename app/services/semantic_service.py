import yaml
from pathlib import Path
from app.models.semantic import SemanticLayer

class SemanticService:
    def __init__(self, yaml_path: str):
        self.yaml_path = Path(yaml_path)
        self.data: SemanticLayer = self._load_and_validate()

    def _load_and_validate(self) -> SemanticLayer:
        """Loads YAML and validates it against the Pydantic SemanticLayer model."""
        if not self.yaml_path.exists():
            raise FileNotFoundError(f"Semantic YAML file not found at {self.yaml_path}")

        with open(self.yaml_path, 'r') as f:
            raw_data = yaml.safe_load(f)

        return SemanticLayer(**raw_data)

    def get_metrics(self):
        return self.data.metrics

    def get_ambiguous_terms(self):
        return self.data.ambiguous_terms
