import os
import math
import re
from collections import Counter

GUIDELINE_FILES = ["sepsis.txt", "aki.txt", "organ_failure.txt"]


def tokenize(text):
    return re.findall(r"[a-zA-Z]+", text.lower())


def build_vector(tokens):
    return Counter(tokens)


def cosine_similarity(vec1, vec2):
    common = set(vec1.keys()) & set(vec2.keys())
    dot_product = sum(vec1[token] * vec2[token] for token in common)

    norm1 = math.sqrt(sum(value * value for value in vec1.values()))
    norm2 = math.sqrt(sum(value * value for value in vec2.values()))

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)


def create_guideline_index(folder_path="data"):
    index = []

    for file_name in GUIDELINE_FILES:
        file_path = os.path.join(folder_path, file_name)

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        tokens = tokenize(content)
        vector = build_vector(tokens)

        index.append({
            "source": file_name,
            "content": content,
            "vector": vector
        })

    return index


def retrieve_guidelines(query, folder_path="data", top_k=2):
    query_tokens = tokenize(query)
    query_vector = build_vector(query_tokens)

    index = create_guideline_index(folder_path)
    results = []

    for item in index:
        score = cosine_similarity(query_vector, item["vector"])
        results.append({
            "source": item["source"],
            "content": item["content"],
            "score": round(score, 4)
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]
