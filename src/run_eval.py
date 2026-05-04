"""
Lab 7 / Lab 10: Headless evaluation script with CI exit codes.
Scores the agent using a Judge LLM (Groq) for Faithfulness and Answer Relevancy.
Exit 0 = pass, Exit 1 = fail.
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
DATASET_PATH = os.environ.get("EVAL_DATASET_PATH", "test_dataset.json")
THRESHOLD_PATH = os.environ.get("EVAL_THRESHOLD_PATH", "eval_threshold_config.json")

if not GROQ_API_KEY:
    print("ERROR: GROQ_API_KEY not set.")
    sys.exit(1)

from langchain_groq import ChatGroq

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

JUDGE_PROMPT = """You are an evaluation judge for an AI pipeline.

Question: {query}
Reference Answer: {reference}
Agent Answer: {answer}

Score the agent answer on two criteria, each from 0.0 to 1.0:
1. Faithfulness: Does the answer stay factually consistent with the reference? No hallucinations?
2. Relevancy: Does the answer actually address the question asked?

Respond ONLY with valid JSON in this exact format:
{{"faithfulness": 0.0, "relevancy": 0.0}}"""


def get_agent_answer(query: str) -> str:
    """Run the agent pipeline in a lightweight way for evaluation."""
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from rag import get_rag_advice

        context = ""
        try:
            from rag import init_rag
            vectorstore = init_rag()
            docs = vectorstore.similarity_search(query, k=2)
            context = "\n".join([d.page_content for d in docs])
        except Exception:
            context = "AutoSpeechDataset pipeline for Urdu speech dataset generation."

        prompt = f"""You are an assistant for the AutoSpeechDataset project.
Context: {context}

Answer this question concisely: {query}"""
        response = llm.invoke(prompt)
        return response.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"


def score_pair(query: str, reference: str, answer: str) -> dict:
    prompt = JUDGE_PROMPT.format(query=query, reference=reference, answer=answer)
    try:
        response = llm.invoke(prompt)
        raw = response.content.strip()
        # Extract JSON even if there's surrounding text
        start = raw.find("{")
        end = raw.rfind("}") + 1
        scores = json.loads(raw[start:end])
        return {
            "faithfulness": float(scores.get("faithfulness", 0.0)),
            "relevancy": float(scores.get("relevancy", 0.0)),
        }
    except Exception as e:
        print(f"  Judge error: {e}")
        return {"faithfulness": 0.0, "relevancy": 0.0}


def main():
    # Load dataset
    dataset_file = Path(DATASET_PATH)
    if not dataset_file.exists():
        print(f"ERROR: Dataset not found at {DATASET_PATH}")
        sys.exit(1)

    with open(dataset_file, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    # Load thresholds
    threshold_file = Path(THRESHOLD_PATH)
    if threshold_file.exists():
        with open(threshold_file, "r") as f:
            thresholds = json.load(f)
    else:
        thresholds = {"min_faithfulness": 0.7, "min_relevancy": 0.7}

    min_faith = thresholds.get("min_faithfulness", 0.7)
    min_rel = thresholds.get("min_relevancy", 0.7)

    print(f"Running evaluation on {len(dataset)} test cases...")
    print(f"Thresholds — Faithfulness: {min_faith}, Relevancy: {min_rel}\n")

    results = []
    for i, item in enumerate(dataset):
        query = item["query"]
        reference = item["reference"]
        print(f"[{i+1}/{len(dataset)}] {query[:60]}...")
        answer = get_agent_answer(query)
        scores = score_pair(query, reference, answer)
        results.append({
            "query": query,
            "reference": reference,
            "answer": answer,
            **scores,
        })
        print(f"  Faithfulness: {scores['faithfulness']:.2f}  Relevancy: {scores['relevancy']:.2f}")

    avg_faith = sum(r["faithfulness"] for r in results) / len(results)
    avg_rel = sum(r["relevancy"] for r in results) / len(results)

    print(f"\n=== Evaluation Results ===")
    print(f"Average Faithfulness : {avg_faith:.3f}  (threshold: {min_faith})")
    print(f"Average Relevancy    : {avg_rel:.3f}  (threshold: {min_rel})")

    # Save report
    report = {
        "total_cases": len(results),
        "avg_faithfulness": round(avg_faith, 3),
        "avg_relevancy": round(avg_rel, 3),
        "thresholds": thresholds,
        "passed": avg_faith >= min_faith and avg_rel >= min_rel,
        "results": results,
    }
    with open("eval_results.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print("Full results saved to eval_results.json")

    if avg_faith < min_faith or avg_rel < min_rel:
        print("\nFAIL: Scores below threshold. Build rejected.")
        sys.exit(1)
    else:
        print("\nPASS: All scores above threshold. Build approved.")
        sys.exit(0)


if __name__ == "__main__":
    main()
