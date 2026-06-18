from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class MetricDefinition(BaseModel):
    name: str
    label: str
    description: str
    grain: str
    base_table: str
    numerator: Optional[str] = None
    denominator: Optional[str] = None
    filters: List[str] = Field(default_factory=list)
    joins: List[str] = Field(default_factory=list)
    caveats: List[str] = Field(default_factory=list)
    owner: str
    certified: bool = False
    last_validated: Optional[datetime] = None

class AmbiguousTerm(BaseModel):
    term: str
    candidates: List[str]
    clarification: str

class SemanticLayer(BaseModel):
    metrics: List[MetricDefinition]
    ambiguous_terms: List[AmbiguousTerm]

class ContextPacket(BaseModel):
    question: str
    retrieved_metrics: List[MetricDefinition]
    join_paths: List[str]
    business_caveats: List[str]
    suggested_sql: Optional[str] = None
