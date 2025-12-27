# evaluation/metrics.py

from typing import List, Dict


def recall_at_k(
    retrieved_sources: List[str],
    relevant_sources: List[str],
    k: int,
) -> float:
    if not relevant_sources:
        return 0.0

    retrieved_k = set(retrieved_sources[:k])
    relevant = set(relevant_sources)

    return 1.0 if retrieved_k.intersection(relevant) else 0.0


def precision_at_k(
    retrieved_sources: List[str],
    relevant_sources: List[str],
    k: int,
) -> float:
    if k == 0:
        return 0.0

    retrieved_k = retrieved_sources[:k]
    relevant = set(relevant_sources)

    relevant_count = sum(1 for src in retrieved_k if src in relevant)
    return relevant_count / k


def mean_reciprocal_rank(
    retrieved_sources: List[str],
    relevant_sources: List[str],
) -> float:
    """
    MRR: How early does the first relevant document appear?
    """

    relevant = set(relevant_sources)

    for idx, src in enumerate(retrieved_sources):
        if src in relevant:
            return 1.0 / (idx + 1)

    return 0.0


def evaluate_query(
    *,
    retrieved_sources: List[str],
    synthesized_sources: List[str],
    relevant_sources: List[str],
    k: int = 5,
) -> Dict[str, float]:
    """
    Evaluate retrieval quality before and after synthesis.
    """

    return {
        # Raw retrieval metrics
        "recall@k_raw": recall_at_k(retrieved_sources, relevant_sources, k),
        "precision@k_raw": precision_at_k(retrieved_sources, relevant_sources, k),
        "mrr": mean_reciprocal_rank(retrieved_sources, relevant_sources),

        # Post-synthesis metrics
        "precision@k_synth": precision_at_k(
            synthesized_sources, relevant_sources, k=1
        ),
    }
