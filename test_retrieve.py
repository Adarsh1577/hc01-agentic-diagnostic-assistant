from rag.retrieve import retrieve_guidelines

query = "lactate hypotension sepsis creatinine"
results = retrieve_guidelines(query)

print("=== RETRIEVAL RESULTS ===")
for r in results:
    print(f"\nSource: {r['source']}")
    print(f"Score: {r['score']}")
    print(r["content"])