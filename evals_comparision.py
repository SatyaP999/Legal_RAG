import pandas as pd
import matplotlib.pyplot as plt

from langsmith import Client
from dotenv import load_dotenv
load_dotenv()

client = Client()



df_header_only = client.get_test_results(project_name="rag-doc-relevance-39424567")
df_header_recursive = client.get_test_results(project_name="rag-doc-relevance-74ba597f")

df_header_only["strategy"] = "header_only"
df_header_recursive["strategy"] = "header_then_recursive"

combined = pd.concat([df_header_only, df_header_recursive])
combined.groupby("strategy")[[
    "feedback.correctness", "feedback.relevance",
    "feedback.groundedness", "feedback.retrieval_relevance"
]].mean()
columns = [
    'strategy',
    # 'feedback.correctness',
    'feedback.relevance',
    'feedback.groundedness',
    'feedback.retrieval_relevance'
]
final_combined = combined[columns].groupby('strategy').mean()

final_combined.plot(kind="bar", figsize=(8,5), ylim=(0,1))
plt.title("RAG Evaluation: header_only vs header_then_recursive")
plt.ylabel("Mean Score")
plt.xticks(rotation=0)
plt.legend(title="Metric", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.savefig("strategy_comparison.png")
plt.show()
