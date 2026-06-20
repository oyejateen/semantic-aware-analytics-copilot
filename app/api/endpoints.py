from fastapi import APIRouter, HTTPException
from app.core.services import services as service_container
from app.models.semantic import ContextPacket

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "healthy"}

@router.get("/search")
async def search_metrics(query: str):
    if not service_container.rag_service or not service_container.semantic_service:
        raise HTTPException(status_code=500, detail="Services not initialized")

    metric_names = service_container.rag_service.retrieve_metrics(query)
    all_metrics = {m.name: m for m in service_container.semantic_service.get_metrics()}
    results = [all_metrics[name].dict() for name in metric_names if name in all_metrics]

    return {"query": query, "results": results}

@router.post("/ask")
async def ask_question(query: str):
    if not service_container.rag_service or not service_container.semantic_service or not service_container.llm_service:
        raise HTTPException(status_code=500, detail="Services not initialized")

    # 1. Ambiguity Detection (RAG-first approach for high concurrency)
    # Step A: Fast Vector Search for ambiguity
    ambiguous_term_name = service_container.rag_service.check_ambiguity(query)

    if ambiguous_term_name:
        # Map the retrieved name back to the AmbiguousTerm object
        ambiguous_term = next((t for t in service_container.semantic_service.get_ambiguous_terms()
                               if t.term == ambiguous_term_name), None)
        if ambiguous_term:
            return {
                "status": "ambiguous",
                "term": ambiguous_term.term,
                "clarification": ambiguous_term.clarification,
                "candidates": ambiguous_term.candidates
            }

    # Step B: Fallback to LLM for complex/vague semantic ambiguity ONLY if RAG didn't find a direct match
    ambiguous_term = service_container.llm_service.detect_ambiguity(
        query, service_container.semantic_service.get_ambiguous_terms()
    )
    if ambiguous_term:
        return {
            "status": "ambiguous",
            "term": ambiguous_term.term,
            "clarification": ambiguous_term.clarification,
            "candidates": ambiguous_term.candidates
        }

    # 2. Semantic Retrieval
    metric_names = service_container.rag_service.retrieve_metrics(query)
    all_metrics = {m.name: m for m in service_container.semantic_service.get_metrics()}
    retrieved_metrics = [all_metrics[name] for name in metric_names if name in all_metrics]

    # 3. Context Packet Assembly
    # Flatten join_paths: each m.joins is a list[str], we want a flat list[str]
    all_joins = []
    for m in retrieved_metrics:
        if m.joins:
            all_joins.extend(m.joins)

    packet = ContextPacket(
        question=query,
        retrieved_metrics=retrieved_metrics,
        join_paths=all_joins,
        business_caveats=[c for m in retrieved_metrics for c in m.caveats]
    )

    # 4. SQL Generation
    sql = service_container.llm_service.generate_sql(packet)

    return {
        "status": "success",
        "sql": sql,
        "context": {
            "metrics": [m.dict() for m in retrieved_metrics],
            "caveats": packet.business_caveats
        }
    }




