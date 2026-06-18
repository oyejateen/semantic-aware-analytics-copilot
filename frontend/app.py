import pandas as pd
import requests
import streamlit as st

# Configuration
BACKEND_URL = "http://localhost:8000"


def main():
    st.set_page_config(page_title="Kona: You analytics buddy", layout="wide")

    with st.sidebar:
        st.title("Kona: You analytics buddy")
        st.write(
            "Ask questions, resolve metric ambiguity, and explore the semantic layer."
        )
        st.caption(
            "Use the AI Assistant tab for chat and the Metric Explorer tab for metric lookup."
        )

        def clear_chat_history():
            st.session_state.messages = [
                {"role": "assistant", "content": "How may I assist you today?"}
            ]
            st.session_state.ambiguity_state = None
            st.session_state.last_context = None
            st.session_state.pending_query = None

        st.button(
            "Clear chat history", on_click=clear_chat_history, use_container_width=True
        )

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "ambiguity_state" not in st.session_state:
        st.session_state.ambiguity_state = None
    if "last_context" not in st.session_state:
        st.session_state.last_context = None
    if "pending_query" not in st.session_state:
        st.session_state.pending_query = None

    tab1, tab2 = st.tabs(["AI Assistant", "Metric Explorer"])

    with tab1:
        st.markdown("### Ask me anything")

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if st.session_state.pending_query:
            with st.spinner("Processing..."):
                handle_backend_response(st.session_state.pending_query)

        if st.session_state.ambiguity_state:
            render_ambiguity_resolution()

    with tab2:
        handle_search()

    if prompt := st.chat_input("Ask a business question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.pending_query = prompt
        st.rerun()


def handle_backend_response(query):
    try:
        response = requests.post(f"{BACKEND_URL}/ask", params={"query": query})
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "ambiguous":
            st.session_state.ambiguity_state = {
                "term": data.get("term"),
                "clarification": data.get("clarification"),
                "candidates": normalize_candidates(data.get("candidates")),
                "original_query": query,
            }
            st.session_state.pending_query = None
            st.rerun()

        elif data.get("status") == "success":
            sql = data.get("sql")
            context = data.get("context", {})
            metrics = context.get("metrics", [])
            caveats = context.get("caveats", [])

            clean_sql = sql.replace("```sql", "").replace("```", "").strip()
            response_content = (
                f"### ✅ Result\n\n**Generated SQL:**\n```sql\n{clean_sql}\n```"
            )

            if metrics:
                metric_names = ", ".join([m.get("name", "Unknown") for m in metrics])
                response_content += f"\n\n**Used Metrics:** `{metric_names}`"

            if caveats:
                response_content += "\n\n**Business Caveats:**\n- " + "\n- ".join(
                    caveats
                )

            st.session_state.messages.append(
                {"role": "assistant", "content": response_content}
            )
            st.session_state.last_context = {"metrics": metrics, "caveats": caveats}
            st.session_state.ambiguity_state = None
            st.session_state.pending_query = None
            st.rerun()
        else:
            st.session_state.pending_query = None

    except Exception as e:
        st.session_state.pending_query = None
        st.error(f"Backend Error: {e}")


def normalize_candidates(raw_candidates):
    if not raw_candidates:
        return []
    if isinstance(raw_candidates, str):
        return [raw_candidates]

    normalized = []
    for item in raw_candidates:
        if isinstance(item, dict):
            label = item.get("name") or item.get("value") or item.get("label")
            normalized.append(str(label) if label is not None else str(item))
        else:
            normalized.append(str(item))

    # Preserve order while dropping duplicates/empties.
    seen = set()
    result = []
    for candidate in normalized:
        value = candidate.strip()
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def fallback_candidates_for_term(term):
    term = (term or "").strip().lower()
    if term == "availability":
        return ["occupancy_rate", "available_nights"]
    if term == "revenue":
        return ["avg_nightly_rate", "revenue_per_available_night"]
    if term == "activity":
        return ["review_velocity", "occupancy_rate"]
    return []


def rewrite_query_for_candidate(original_query, ambiguous_term, candidate):
    rewritten = original_query.replace(ambiguous_term, candidate)
    rewritten = rewritten.replace(ambiguous_term.title(), candidate)
    rewritten = rewritten.replace(ambiguous_term.upper(), candidate)
    if rewritten == original_query:
        return candidate.replace("_", " ")
    return rewritten


def render_ambiguity_resolution():
    state = st.session_state.ambiguity_state
    candidates = normalize_candidates(state.get("candidates", []))
    fallback_candidates = fallback_candidates_for_term(state.get("term"))

    for candidate in fallback_candidates:
        if candidate not in candidates:
            candidates.append(candidate)

    st.info(f"⚠️ {state['term']}: {state['clarification']}")

    if not candidates:
        st.warning(
            "No options were returned for this ambiguity. Please try rephrasing."
        )
        return

    cols = st.columns(min(len(candidates), 4))
    for idx, candidate in enumerate(candidates):
        with cols[idx % len(cols)]:
            if st.button(
                f"📌 {candidate}",
                key=f"cand_{candidate}",
                use_container_width=True,
            ):
                refined_query = rewrite_query_for_candidate(
                    state["original_query"], state["term"], candidate
                )
                if (
                    st.session_state.messages
                    and st.session_state.messages[-1]["role"] == "user"
                ):
                    st.session_state.messages[-1] = {
                        "role": "user",
                        "content": refined_query,
                    }
                else:
                    st.session_state.messages.append(
                        {"role": "user", "content": refined_query}
                    )
                st.session_state.ambiguity_state = None
                st.session_state.pending_query = refined_query
                st.rerun()


def handle_search():
    st.subheader("Metric Explorer")
    query = st.text_input("Search for metrics (e.g., 'revenue', 'churn')")
    if query:
        try:
            resp = requests.get(f"{BACKEND_URL}/search", params={"query": query})
            resp.raise_for_status()
            data = resp.json()
            results = data.get("results", [])

            if results:
                # Use a DataFrame for a cleaner table view
                df_data = []
                for item in results:
                    df_data.append(
                        {
                            "Metric": item["name"],
                            "Definition": item.get("description", "N/A"),
                            "Caveats": (
                                ", ".join(item.get("caveats", []))
                                if isinstance(item.get("caveats"), list)
                                else item.get("caveats", "N/A")
                            ),
                        }
                    )
                df = pd.DataFrame(df_data)
                st.table(df)
            else:
                st.info("No matching metrics found.")
        except Exception as e:
            st.error(f"Error: {e}")


if __name__ == "__main__":
    main()
