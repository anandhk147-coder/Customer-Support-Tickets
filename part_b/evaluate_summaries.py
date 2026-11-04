"""
Module: evaluate_summaries.py
Computes quantitative overlap and qualitative rubric evaluations
for LLM-generated summaries against reference summaries.
"""

from typing import Dict, List, Any
import re


def tokenize(text: str) -> List[str]:
    """Tokenize and normalize text into lower-case alphanumeric tokens."""
    return re.findall(r"\b[a-zA-Z0-9_%-]+\b", text.lower())


def compute_token_metrics(reference: str, candidate: str) -> Dict[str, float]:
    ref_tokens = tokenize(reference)
    cand_tokens = tokenize(candidate)

    ref_set = set(ref_tokens)
    cand_set = set(cand_tokens)

    intersection = ref_set.intersection(cand_set)
    union = ref_set.union(cand_set)

    precision = len(intersection) / len(cand_set) if cand_set else 0.0
    recall = len(intersection) / len(ref_set) if ref_set else 0.0
    f1 = (
        (2 * precision * recall) / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )
    jaccard = len(intersection) / len(union) if union else 0.0

    return {
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3),
        "jaccard": round(jaccard, 3),
    }


def evaluate_all():
    tickets_eval = [
        {
            "ticket_id": "T1",
            "reference": "Customer locked out of CloudSync after resetting their password.",
            "llm": "User cannot log in to CloudSync.",
            "rubric": {
                "factual_accuracy": 5.0,
                "information_completeness": 3.0,
                "entity_attribution": 5.0,
                "conciseness_utility": 4.0,
            },
            "justification": (
                "Accurate, but omitted causal trigger ('after resetting their password')."
            ),
        },
        {
            "ticket_id": "T2",
            "reference": "CloudSync sync process hangs near completion.",
            "llm": "Sync is stuck.",
            "rubric": {
                "factual_accuracy": 5.0,
                "information_completeness": 1.5,
                "entity_attribution": 1.0,
                "conciseness_utility": 2.0,
            },
            "justification": (
                "Severe loss of context. Omitted product entity ('CloudSync') and completion stage ('90%' / 'near completion')."
            ),
        },
        {
            "ticket_id": "T3",
            "reference": "InvoicePro-generated PDFs are missing invoice line items.",
            "llm": "PDF export has a missing items bug in InvoicePro.",
            "rubric": {
                "factual_accuracy": 4.8,
                "information_completeness": 4.5,
                "entity_attribution": 5.0,
                "conciseness_utility": 4.8,
            },
            "justification": (
                "Preserved product, subsystem, and symptom. High triage value."
            ),
        },
    ]

    weights = {
        "factual_accuracy": 0.30,
        "information_completeness": 0.35,
        "entity_attribution": 0.20,
        "conciseness_utility": 0.15,
    }

    print("=" * 80)
    print(" PART B.1: LLM SUMMARY EVALUATION (RUBRIC & TOKEN METRICS)")
    print("=" * 80)

    for item in tickets_eval:
        r = item["rubric"]
        composite = sum(r[dim] * weights[dim] for dim in weights)
        pct = (composite / 5.0) * 100

        token_metrics = compute_token_metrics(item["reference"], item["llm"])

        print(f"\n[Ticket {item['ticket_id']}]")
        print(f"  Reference : \"{item['reference']}\"")
        print(f"  LLM       : \"{item['llm']}\"")
        print(f"  Rubric Breakdown (out of 5.0):")
        print(f"    - Factual Accuracy (30%)     : {r['factual_accuracy']}")
        print(f"    - Completeness (35%)         : {r['information_completeness']}")
        print(f"    - Entity Attribution (20%)   : {r['entity_attribution']}")
        print(f"    - Conciseness/Utility (15%)  : {r['conciseness_utility']}")
        print(f"  ==> Composite Score: {composite:.2f} / 5.0 ({pct:.1f}%)")
        print(f"  Token Overlap Metrics: F1={token_metrics['f1']}, Recall={token_metrics['recall']}, Precision={token_metrics['precision']}, Jaccard={token_metrics['jaccard']}")
        print(f"  Justification: {item['justification']}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    evaluate_all()
