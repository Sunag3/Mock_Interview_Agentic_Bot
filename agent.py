import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from tools import detect_filler_words, check_star_structure, score_relevance

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

QUESTION_BANK = [
    {
        "type": "behavioral",
        "question": "Tell me about a time you had to deal with a tight project deadline under pressure.",
        "keywords": ["deadline", "priority", "communication", "delivery", "teamwork", "trade-off"]
    },
    {
        "type": "behavioral",
        "question": "Describe a situation where you had a major disagreement with a teammate or stakeholder. How did you resolve it?",
        "keywords": ["disagreement", "conflict", "listened", "compromise", "resolution", "collaboration"]
    },
    {
        "type": "technical",
        "question": "How do you approach debugging a high-severity production outage or critical bug?",
        "keywords": ["logs", "reproduce", "root cause", "monitoring", "isolation", "post-mortem", "mitigation"]
    },
    {
        "type": "general",
        "question": "Why are you interested in this position, and what unique value do you bring to our team?",
        "keywords": ["skills", "impact", "growth", "mission", "experience", "value"]
    }
]

def evaluate_answer(candidate_answer: str, question_info: dict) -> dict:
    """Runs evaluation tools on candidate answer."""
    fillers = detect_filler_words(candidate_answer)
    star = check_star_structure(candidate_answer) if question_info["type"] == "behavioral" else None
    relevance = score_relevance(candidate_answer, question_info["keywords"])

    return {
        "fillers": fillers,
        "star": star,
        "relevance": relevance
    }

def generate_encouraging_feedback(candidate_answer: str, question_info: dict, eval_results: dict) -> str:
    """Generates encouraging, concise feedback using the LLM."""
    prompt = f"""
    You are InterviewIQ, an encouraging AI interview coach.
    Question Asked: "{question_info['question']}"
    Candidate Answer: "{candidate_answer}"
    Evaluation Tools Output: {json.dumps(eval_results)}

    Generate short, encouraging, and constructive feedback directly addressing the candidate.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def answer_meta_question(coach_query: str, eval_history: list) -> str:
    """Answers candidate meta-questions using entire session memory."""
    prompt = f"""
    You are InterviewIQ Coach. The candidate is asking a meta-question about their session progress.
    Candidate Meta-Question: "{coach_query}"
    
    Session Evaluation History across all questions answered so far:
    {json.dumps(eval_history, indent=2)}

    Answer the candidate's question specifically and constructively using the whole session context.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def generate_session_report(eval_history: list) -> str:
    """Creates aggregated summary report for session conclusion."""
    total_relevance = sum(item["evals"]["relevance"]["relevance_score"] for item in eval_history)
    avg_relevance = round(total_relevance / len(eval_history), 2)
    total_fillers = sum(item["evals"]["fillers"]["total_fillers"] for item in eval_history)

    prompt = f"""
    Synthesize a final session report for InterviewIQ candidate based on all turns.
    Session History Data:
    {json.dumps(eval_history, indent=2)}

    Average Relevance Score: {avg_relevance}%
    Total Filler Words Used: {total_fillers}

    Provide a well-structured Markdown summary with:
    1. **Average Relevance & Delivery Overview**
    2. **Weakest Area Identified** (e.g. STAR completeness, filler usage, concept depth)
    3. **Key Strengths**
    4. **Actionable Recommendations for Real Interviews**
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content