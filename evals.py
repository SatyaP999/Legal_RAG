import os
from dotenv import load_dotenv

from langsmith import Client
from langchain_openai import ChatOpenAI

from document_rag import build_rag_chain, build_rag_chain_hyrid
from prompts import (
    correctness_instructions,
    grounded_instructions,
    retrieval_relevance_instructions,
    relevance_instructions
)
from models import *
from evals_dataset import examples

client = Client()

load_dotenv()
LLM_KEY = os.getenv("AI_CREDITS_API_KEY", "")

for collection_name in ["header_only", "header_then_recursive"]:

    dataset_name = f"Legal doc hybrid Q&A - {collection_name} - reranked"
    dataset = client.create_dataset(dataset_name=dataset_name)
    client.create_examples(
        dataset_id=dataset.id,
        examples=examples
    )

    def precision_at_k(retrieved, relevant, k):
        retrieved_k = retrieved[:k]
        hits = len(set(retrieved_k) & set(relevant))
        return hits/k

    def relevant_at_k(retrieved, relevant, k):
        retrieved_k = retrieved[:k]
        hits = len(set(retrieved_k) & set(relevant))
        return hits / len(relevant) if relevant else 0.0

    def hit_rate_at_k(retrieved, relevant, k):
        retrieved_k = retrieved[:k]
        return 1.0 if set(retrieved_k) & set(relevant) else 0.0

    def reciprocal_rank(retrieved, relevant):
        for i, doc_id in enumerate(retrieved, start=1):
            if doc_id in relevant:
                return 1.0 / i

    def mrr(all_retreieved, all_relevant):
        rr_scores = [reciprocal_rank(ret, rel) for ret, rel in zip(all_retreieved, all_relevant)]
        return sum(rr_scores) / len(rr_scores)


    def average_precision(retrieved, relevant):
        if not relevant:
            return 0.0

        hits = 0
        sum_precisions = 0.0
        for i, doc_id in enumerate(retrieved, start=1):
            if doc_id in relevant:
                hits += 1
                precision_at_i = hits/i
                sum_precisions += precision_at_i

        return sum_precisions / len(relevant)

    def map(all_retreieved, all_relevant):
        ap_values = [average_precision(ret, rel) for ret, rel in zip(all_retreieved, all_relevant)]
        return sum(ap_values) / len(ap_values)


    def correctness(
            inputs: dict,
            outputs: dict,
            reference_outputs: dict
    ) -> bool:
        answers = f"""\
    QUESTION: {inputs['question']}
    GROUND TURTH ANSWER: {reference_outputs['answer']}
    STUDENT_ANSWER: {outputs['answer']}"""
        grader_llm = ChatOpenAI(
            model="openai/gpt-4o-mini",
            base_url="https://api.aicredits.in/v1",
            api_key=LLM_KEY,
        ).with_structured_output(
            CorrectenssGrade,
            method="json_schema",
            strict=True
        )
        grade = grader_llm.invoke([
            {"role": "system", "content": correctness_instructions},
            {"role": "user", "content": answers}
        ])

        return grade["correct"]

    def relevance(
            inputs: dict,
            outputs: dict
    ) -> bool:
        answer = f"""\
    QUESTION: {inputs['question']}
    STUDENT ANSWER: {outputs['answer']}
    """
        relevance_llm = ChatOpenAI(
            model="openai/gpt-4o-mini",
            base_url="https://api.aicredits.in/v1",
            api_key=LLM_KEY,
        ).with_structured_output(
            RelevanceGrade,
            method="json_schema",
            strict=True
        )

        grade = relevance_llm.invoke([
            {"role": "system", "content": relevance_instructions},
            {"role": "user", "content": answer}
        ])
        return grade['relevant']

    def groundedness(
            inputs: dict,
            outputs: dict
    ) -> bool:
        doc_string = "\n\n".join(doc.page_content for doc in outputs["documents"])
        answer = f"FACTS: {doc_string}\nSTUDENT ANSWER: {outputs['answer']}"

        grounded_llm = ChatOpenAI(
            model="openai/gpt-4o-mini",
            base_url="https://api.aicredits.in/v1",
            api_key=LLM_KEY,
        ).with_structured_output(
            GroundedGrade,
            method="json_schema",
            strict=True
        )

        grade = grounded_llm.invoke([
            {"role": "system", "content": grounded_instructions},
            {"role": "user", "content": answer}
        ])
        return grade['grounded']

    def retrieval_relevance(
            inputs: dict,
            outputs: dict
    ) -> bool:
        doc_string = "\n\n".join(doc.page_content for doc in outputs["documents"])
        answer = f"FACTS: {doc_string}\nSTUDENT ANSWER: {outputs['answer']}"

        retrieval_relevance_llm = ChatOpenAI(
            model="openai/gpt-4o-mini",
            base_url="https://api.aicredits.in/v1",
            api_key=LLM_KEY,
        ).with_structured_output(
            RetrievalRelevanceGrade,
            method="json_schema",
            strict=True
        )

        grade = retrieval_relevance_llm.invoke([
            {"role": "system", "content": retrieval_relevance_instructions},
            {"role": "user", "content": answer}
        ])
        return grade['relevant']

    def target(inputs: dict) -> dict:

        result = build_rag_chain_hyrid(
            collection_name=collection_name,
            question=inputs["question"]
        )
        return result

    experiment_results = client.evaluate(
        target,
        data=dataset_name,
        evaluators=[correctness, relevance, groundedness, retrieval_relevance],
        experiment_prefix="rag-doc-relevance",
        metadata={"version": "LCEL context, gpt-4-0125-preview"},
    )


