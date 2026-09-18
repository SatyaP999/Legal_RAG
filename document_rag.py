import os
import pickle
from dotenv import load_dotenv
from pathlib import Path


from langsmith import traceable
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever


from variables import MD_PATH
from vectorstore import get_vectorstore
from prompts import RAG_PROMPT

load_dotenv()
LLM_KEY = os.getenv("AI_CREDITS_API_KEY", "")
CHUNKS_DIR = Path("./chunk_store")

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def get_llm():
    return ChatOpenAI(
        model="openai/gpt-4o-mini",
        base_url="https://api.aicredits.in/v1",
        api_key=LLM_KEY,
    )
_bm25_cache: dict[str, BM25Retriever] = {}

def get_bm25(
        collection_name: str,
        top_k: int = 6,

) -> BM25Retriever:
    if collection_name not in _bm25_cache:
        chunks_path = CHUNKS_DIR / f"{collection_name}.pkl"
        if not chunks_path.exists():
            raise FileNotFoundError(
                f"No chunks found for '{collection_name}' - run document_indexing.py first."
            )

        with open(chunks_path, "rb") as f:
            chunks = pickle.load(f)
        
        bm_25 = BM25Retriever.from_documents(chunks)
        bm_25.k = top_k

        _bm25_cache[collection_name] = bm_25

    return _bm25_cache[collection_name]



@traceable
def build_rag_chain(collection_name: str, question: str):

    vectorstore = get_vectorstore(
        collection_name=collection_name
    )

    # Retrieve documents
    def retrieve_documents(query: str):
        docs_with_scores = (
            vectorstore.similarity_search_with_relevance_scores(
                query,
                k=6,
                score_threshold=0.5
            )
        )
        return [
            doc
            for doc, score in docs_with_scores
        ]



    # Extract actual documents
    documents = retrieve_documents(question)

    # Format context
    context = "\n\n".join(
        doc.page_content
        for doc in documents
    )

    #llm
    llm = get_llm()

    # Generation chain
    rag_chain = (
        RAG_PROMPT
        | llm
        | StrOutputParser()
    )

    # Generate answer
    answer = rag_chain.invoke({
        "context": context,
        "question": question
    })

    # Return both
    return {
        "answer": answer,
        "documents": documents
    }

@traceable
def build_rag_chain_hyrid(
    collection_name: str,
    question: str
):
    vectorstore = get_vectorstore(
        collection_name=collection_name
    )

    dense_retreiver = vectorstore.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"k": 6, "score_threshold": 0.5},
    )

    bm25_retriever = get_bm25(collection_name=collection_name)

    ensemble_retriever = EnsembleRetriever(
        retrievers=[dense_retreiver, bm25_retriever],
        weights=[0.6, 0.4]
    )

    documents = ensemble_retriever.invoke(question)
    context = "\n\n".join(doc.page_content for doc in documents)

    llm = get_llm()
    rag_chain = RAG_PROMPT | llm | StrOutputParser()
    answer = rag_chain.invoke({"context": context, "question": question})

    return {"answer": answer, "documents": documents}


if __name__ == "__main__":
    ans = build_rag_chain_hyrid(
        collection_name="header_only",
        question="When did BIA dismissed the appeal and  adopted "
        "and affirmed the IJ's adverse credibility finding?"
    )


    print(f"ANSWER: {ans['answer']}\n")
    print(f"DOCUMENTS: {ans['documents']}")