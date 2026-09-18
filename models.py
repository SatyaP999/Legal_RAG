from typing_extensions import TypedDict, Annotated

class CorrectenssGrade(TypedDict):
    explanation: Annotated[str, ..., "Explain your reasoning for the score."]
    correct: Annotated[str, ..., "True if the answer is correct, False otherwise."]

class RelevanceGrade(TypedDict):
    explanation: Annotated[str, ..., "Explain your reasoning for the score"]
    relevant: Annotated[
        bool, ..., "Provide the score on whether the answer addresses the question"
    ]

class GroundedGrade(TypedDict):
    explanation: Annotated[str, ..., "Explain the reasoning for the score."]
    grounded: Annotated[bool,
                        ..., "Provide the score on if the answer hallucinates from the documents"]

class RetrievalRelevanceGrade(TypedDict):
    explanation: Annotated[str, ..., "Explain your reasoning for the score"]
    relevant: Annotated[
        bool,
        ...,
        "True if the retrieved documents are relevant to the question, False otherwise",
    ]