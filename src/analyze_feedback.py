"""
Lab 11: Drift Monitor — analyzes negative feedback using a Judge LLM.
Categorizes failures and prints a drift report.
"""

import os
import json
from dotenv import load_dotenv
from feedback_db import init_db, get_negative_feedback, get_all_feedback

load_dotenv()

from langchain_groq import ChatGroq

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

CATEGORY_PROMPT = """You are a quality analyst for an AI pipeline.

A user gave a thumbs-down to this interaction:

User Input: {user_input}
Agent Response: {agent_response}
User Comment: {comment}

Categorize the failure into exactly ONE of these categories:
- Hallucination: The agent made up facts not grounded in reality
- Tool Error: The agent failed to use the correct tool or used wrong arguments
- Wrong Tone: The response was unhelpful, rude, or off-topic
- Incomplete Response: The agent gave a partial or truncated answer
- Pipeline Failure: A technical error occurred during processing
- Other: Does not fit the above categories

Respond ONLY with valid JSON:
{{"category": "<category>", "reason": "<one sentence explanation>"}}"""


def categorize_failure(entry: dict) -> dict:
    prompt = CATEGORY_PROMPT.format(
        user_input=entry["user_input"],
        agent_response=entry["agent_response"],
        comment=entry.get("optional_comment") or "No comment provided",
    )
    try:
        response = llm.invoke(prompt)
        raw = response.content.strip()
        start = raw.find("{")
        end = raw.rfind("}") + 1
        result = json.loads(raw[start:end])
        return result
    except Exception as e:
        return {"category": "Other", "reason": f"Could not categorize: {e}"}


def main():
    init_db()
    all_feedback = get_all_feedback()
    negative = get_negative_feedback()

    total = len(all_feedback)
    neg_count = len(negative)

    if total == 0:
        print("No feedback logged yet.")
        return

    print(f"Total interactions: {total}")
    print(f"Negative feedback:  {neg_count} ({100*neg_count/total:.1f}%)\n")

    if neg_count == 0:
        print("No negative feedback to analyze.")
        return

    print("Analyzing failures with Judge LLM...\n")

    category_counts: dict[str, int] = {}
    categorized = []

    for entry in negative:
        result = categorize_failure(entry)
        cat = result.get("category", "Other")
        reason = result.get("reason", "")
        category_counts[cat] = category_counts.get(cat, 0) + 1
        categorized.append({**entry, "category": cat, "reason": reason})
        print(f"  [{cat}] {entry['user_input'][:60]}...")
        print(f"         → {reason}\n")

    print("=== Drift Report ===")
    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        pct = 100 * count / neg_count
        print(f"  {cat}: {count} ({pct:.1f}% of failures)")

    # Save report
    report_lines = [
        "# Drift Report\n",
        f"Total interactions logged: {total}",
        f"Negative feedback: {neg_count} ({100*neg_count/total:.1f}%)\n",
        "## Failure Categories\n",
    ]
    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        pct = 100 * count / neg_count
        report_lines.append(f"- **{cat}**: {count} cases ({pct:.1f}% of failures)")

    report_lines.append("\n## Detailed Failures\n")
    for entry in categorized:
        report_lines.append(f"### [{entry['category']}] {entry['timestamp']}")
        report_lines.append(f"- Input: {entry['user_input']}")
        report_lines.append(f"- Reason: {entry['reason']}")
        if entry.get("optional_comment"):
            report_lines.append(f"- User comment: {entry['optional_comment']}")
        report_lines.append("")

    with open("drift_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print("\nDrift report saved to drift_report.md")


if __name__ == "__main__":
    main()
