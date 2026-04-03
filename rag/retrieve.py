import os

def retrieve_guidelines(query, folder_path="data"):
    query_words = set(query.lower().split())
    results = []

    files = ["sepsis.txt", "aki.txt", "organ_failure.txt"]

    for file in files:
        path = os.path.join(folder_path, file)

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        words = set(content.lower().split())
        score = len(query_words.intersection(words))

        results.append({
            "source": file,
            "content": content,
            "score": score
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:2]