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

    dataset_name = f"Legal doc hybrid Q&A - {collection_name}"
    dataset = client.create_dataset(dataset_name=dataset_name)
    client.create_examples(
        dataset_id=dataset.id,
        examples=examples
    )

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


