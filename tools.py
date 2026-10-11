import re
from typing import Dict, List, Any

def detect_filler_words(candidate_response: str) -> Dict[str, Any]:
    """Detects filler words, calculates density, and flags excessive usage."""
    if not candidate_response or not candidate_response.strip():
        return {
            "total_words": 0,
            "total_fillers": 0,
            "filler_ratio": 0.0,
            "filler_counts": {},
            "has_excessive_fillers": False,
            "detected_instances": []
        }

    target_fillers = [
        "um", "uh", "like", "basically", "actually", "literally",
        "you know", "i mean", "so", "kind of", "sort of", "right"
    ]

    lowered_response = candidate_response.lower()
    words = re.findall(r'\b\w+\b', lowered_response)
    total_words = len(words)

    total_fillers = 0
    filler_counts: Dict[str, int] = {}
    detected_instances: List[Dict[str, Any]] = []

    for filler in target_fillers:
        pattern = r'\b' + re.escape(filler) + r'\b'
        matches = list(re.finditer(pattern, lowered_response))
        count = len(matches)

        if count > 0:
            filler_counts[filler] = count
            total_fillers += count
            for match in matches:
                detected_instances.append({
                    "word": filler,
                    "start_char": match.start(),
                    "end_char": match.end()
                })

    detected_instances.sort(key=lambda x: x["start_char"])
    filler_ratio = round(total_fillers / total_words, 4) if total_words > 0 else 0.0
    has_excessive_fillers = filler_ratio > 0.05

    return {
        "total_words": total_words,
        "total_fillers": total_fillers,
        "filler_ratio": filler_ratio,
        "filler_counts": filler_counts,
        "has_excessive_fillers": has_excessive_fillers,
        "detected_instances": detected_instances
    }


def check_star_structure(candidate_response: str) -> Dict[str, Any]:
    """Evaluates presence of Situation, Task, Action, and Result components."""
    if not candidate_response or not candidate_response.strip():
        return {
            "components_detected": {"situation": False, "task": False, "action": False, "result": False},
            "star_completeness_score": 0.0,
            "missing_components": ["situation", "task", "action", "result"],
            "detected_keywords": {},
            "feedback_summary": "No response provided."
        }

    lowered_response = candidate_response.lower()

    patterns = {
        "situation": [r"\b(when i was|at my previous|in my last role|during my time|project at|the company was|we were facing|the challenge was|back in|a few years ago|the background|context)\b"],
        "task": [r"\b(my role was|i was responsible for|i needed to|my goal was|i was tasked with|the objective was|assigned to|had to ensure|our goal was|required me to)\b"],
        "action": [r"\b(i created|i built|i designed|i developed|i organized|i implemented|i led|i took the initiative|i scheduled|i analyzed|i proposed|i stepped in|i resolved|i communicated|i decided to)\b"],
        "result": [r"\b(as a result|consequently|the outcome was|we achieved|i reduced|i increased|i improved|ultimately|in the end|led to a|resulting in|we grew|saved|delivered on time)\b"]
    }

    components_detected = {}
    detected_keywords = {}
    missing_components = []

    for component, regex_list in patterns.items():
        found_signals = []
        for regex in regex_list:
            matches = re.findall(regex, lowered_response)
            if matches:
                found_signals.extend(matches)

        if found_signals:
            components_detected[component] = True
            detected_keywords[component] = list(set(found_signals))
        else:
            components_detected[component] = False
            missing_components.append(component)

    detected_count = sum(1 for present in components_detected.values() if present)
    star_completeness_score = round(detected_count / 4.0, 2)

    if star_completeness_score == 1.0:
        feedback_summary = "Excellent! All four components of the STAR framework are present."
    elif star_completeness_score >= 0.5:
        feedback_summary = f"Good attempt, but missing: {', '.join(missing_components).title()}."
    else:
        feedback_summary = f"Incomplete STAR structure. Missing key sections: {', '.join(missing_components).title()}."

    return {
        "components_detected": components_detected,
        "star_completeness_score": star_completeness_score,
        "missing_components": missing_components,
        "detected_keywords": detected_keywords,
        "feedback_summary": feedback_summary
    }


def score_relevance(candidate_response: str, expected_keywords: List[str]) -> Dict[str, Any]:
    """Scores response relevance (0-100) based on expected keywords."""
    if not candidate_response or not candidate_response.strip() or not expected_keywords:
        return {
            "relevance_score": 0.0,
            "matched_keywords": [],
            "missing_keywords": expected_keywords if expected_keywords else [],
            "match_percentage": 0.0,
            "relevance_tier": "Poor"
        }

    lowered_response = candidate_response.lower()
    matched_keywords = []
    missing_keywords = []

    for keyword in expected_keywords:
        kw_lower = keyword.lower()
        pattern = r'\b' + re.escape(kw_lower) + r'\b'
        if re.search(pattern, lowered_response) or kw_lower in lowered_response:
            matched_keywords.append(keyword)
        else:
            missing_keywords.append(keyword)

    total_expected = len(expected_keywords)
    match_ratio = len(matched_keywords) / total_expected if total_expected > 0 else 0.0
    relevance_score = round(match_ratio * 100.0, 2)

    if relevance_score >= 80:
        relevance_tier = "High"
    elif relevance_score >= 50:
        relevance_tier = "Moderate"
    else:
        relevance_tier = "Low"

    return {
        "relevance_score": relevance_score,
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords,
        "match_percentage": round(match_ratio * 100, 1),
        "relevance_tier": relevance_tier
    }