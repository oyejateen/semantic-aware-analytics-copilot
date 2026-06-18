import os
import yaml
import chromadb


def run_pipeline():
    # 🎯 CONFIGURATION: Adjust this path to match exactly where your file is!
    # If your folder name is different, change 'semantic-aware-analytics-v2' to match your sidebar
    yaml_path = "semantic-aware-analytics-copilot/semantic/all_metrics.yaml"

    # Quick safety check: if the path above is wrong, let's catch it nicely
    if not os.path.exists(yaml_path):
        # Let's try checking the root of the folder just in case
        yaml_path = "semantic-aware-analytics-v2/all_metrics.yaml"
        if not os.path.exists(yaml_path):
            print("❌ Error: Could not find 'all_metrics.yaml'.")
            print(
                "Please check your sidebar and verify the exact folder name and file location!"
            )
            return

    # --- STEP 1: READ THE TEAM'S YAML FILE ---
    print(f"📖 Reading metrics data from: {yaml_path}")
    with open(yaml_path, "r") as f:
        config = yaml.safe_load(f)
        metrics_list = config.get("metrics", [])

    if not metrics_list:
        print("⚠️ The YAML file is empty or missing a 'metrics' section.")
        return

    # --- STEP 2: OPEN THE FILING CABINET (ChromaDB) ---
    print("📁 Opening local ChromaDB storage...")
    client = chromadb.PersistentClient(path="./chroma_db")

    # get_or_create means it won't crash if you run this script multiple times
    collection = client.get_or_create_collection(name="metrics_store")

    # --- STEP 3: PREPARE DATA FOR INDICES ---
    documents = []
    metadatas = []
    ids = []

    for m in metrics_list:
        # We use .get() with a fallback string so missing fields won't cause a crash
        display_name = m.get("display_name", m.get("name", "Unnamed Metric"))
        description = m.get("description", "No description provided.")

        # Safe handling if ambiguous_terms is completely missing or empty
        terms = m.get("ambiguous_terms", [])
        if terms is None:
            terms = []

        combined_text = (
            f"Metric: {display_name}\n"
            f"Description: {description}\n"
            f"Keywords: {', '.join(terms)}"
        )

        documents.append(combined_text)
        metadatas.append(
            {
                "technical_name": m.get("name", "unknown"),
                "certified": str(m.get("certified", False)),
            }
        )
        ids.append(m.get("name", f"metric_{len(ids)}"))

    # --- STEP 4: GENERATE MATH VECTORS & SAVE ---
    print(f"🧬 Transforming {len(ids)} metrics into vectors and saving to ChromaDB...")
    collection.add(documents=documents, metadatas=metadatas, ids=ids)

    print(
        "✅ Pipeline execution successful! Your 'metrics_store' database is ready inside the ./chroma_db folder."
    )


if __name__ == "__main__":
    run_pipeline()
