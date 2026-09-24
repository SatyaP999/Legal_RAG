from sentence_transformers import CrossEncoder

reranker = CrossEncoder(
    "BAAI/bge-reranker-v2-m3"
)

def reranked_chunks(query: str, documents: list[str], top_k: int = 6) -> list[str]:
    reranked_docs = []
    pairs = [
        (query, doc) for doc in documents
    ]

    scores = reranker.predict(pairs)
    for doc, score in sorted(
        zip(documents, scores),
        key = lambda x: x[1],
        reverse=True
    ):
        # print(score, doc)
        reranked_docs.append(doc)
    return reranked_docs[:top_k]

if __name__ == "__main__":
    query = "Can the customer terminate the contract after an SLA breach?"

    documents = [
        "The customer may terminate this agreement for material breach.",
        "The vendor shall maintain 99.9% service availability.",
        "Either party may terminate upon thirty days prior written notice."
    ]

    docs = reranked_chunks(query=query, documents=documents)
    for d in docs:
        print(d, "\n")