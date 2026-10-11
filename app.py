from typing import List, Any
import gradio as gr
from agent import (
    QUESTION_BANK,
    evaluate_answer,
    generate_encouraging_feedback,
    answer_meta_question,
    generate_session_report
)

def format_scorecard_table(eval_history: List[dict]) -> List[List[Any]]:
    """Formats history data for the Gradio Dataframe."""
    table_data = []
    for item in eval_history:
        q_text = item["question"]
        rel_score = f"{item['evals']['relevance']['relevance_score']}%"
        fillers_cnt = item["evals"]["fillers"]["total_fillers"]
        
        star_str = "N/A"
        if item["evals"]["star"]:
            star_score = item["evals"]["star"]["star_completeness_score"]
            star_str = f"{int(star_score * 100)}%"
            
        table_data.append([q_text, rel_score, star_str, fillers_cnt])
    return table_data


def submit_answer(candidate_answer: str, state: dict):
    """Handles answer submission from UI."""
    if not candidate_answer.strip():
        return "Please enter an answer before submitting.", state["scorecard_data"], "", candidate_answer, state

    q_idx = state["current_q_idx"]
    current_q = QUESTION_BANK[q_idx]

    # Evaluate answer with tools & generate feedback
    eval_results = evaluate_answer(candidate_answer, current_q)
    feedback_text = generate_encouraging_feedback(candidate_answer, current_q, eval_results)

    # Save turn in session memory
    session_record = {
        "question": current_q["question"],
        "answer": candidate_answer,
        "evals": eval_results,
        "feedback": feedback_text
    }
    state["eval_history"].append(session_record)

    # Update scorecard table
    scorecard_data = format_scorecard_table(state["eval_history"])
    state["scorecard_data"] = scorecard_data

    # Move to next question if available
    if q_idx + 1 < len(QUESTION_BANK):
        state["current_q_idx"] += 1
        next_q_display = f"**Question {state['current_q_idx'] + 1} of {len(QUESTION_BANK)}:**\n{QUESTION_BANK[state['current_q_idx']]['question']}"
    else:
        next_q_display = "**Interview Complete!** Click 'Generate Final Report' below to view your aggregated insights."

    # Return "" as the 4th element to clear the answer textbox
    return feedback_text, scorecard_data, next_q_display, "", state


def ask_coach(coach_query: str, state: dict):
    """Handles coach Q&A from UI."""
    if not coach_query.strip():
        return "Please type a question for the coach."
    
    if not state["eval_history"]:
        return "No answers have been evaluated yet. Complete at least one question first!"

    return answer_meta_question(coach_query, state["eval_history"])


def generate_report(state: dict):
    """Generates final aggregated summary."""
    if not state["eval_history"]:
        return "No session data found to summarize. Please answer at least one question."

    return generate_session_report(state["eval_history"])


def build_ui():
    initial_state = {
        "current_q_idx": 0,
        "eval_history": [],
        "scorecard_data": []
    }

    with gr.Blocks(title="InterviewIQ - AI Mock-Interview Coach") as demo:
        state = gr.State(initial_state)

        gr.Markdown("# 🚀 InterviewIQ: AI Mock-Interview Coach")
        gr.Markdown("Practice interview questions, receive immediate tool-evaluated feedback, track your performance, and ask your AI Coach for guidance.")

        with gr.Row():
            # Left: Question & Answer Section
            with gr.Column(scale=6):
                gr.Markdown("### 📌 Current Question")
                current_q_box = gr.Markdown(f"**Question 1 of {len(QUESTION_BANK)}:**\n{QUESTION_BANK[0]['question']}")
                
                answer_input = gr.Textbox(
                    lines=5, 
                    placeholder="Type your spoken or written answer here...", 
                    label="Answer Box"
                )
                submit_btn = gr.Button("Submit Answer", variant="primary")

                gr.Markdown("### 💬 Feedback Panel")
                feedback_output = gr.Markdown("Submit an answer above to receive feedback.")

            # Right: Live Scorecard
            with gr.Column(scale=6):
                gr.Markdown("### 📊 Live Scorecard")
                scorecard_table = gr.Dataframe(
                    headers=["Question", "Relevance Score", "STAR Score", "Filler Count"],
                    datatype=["str", "str", "str", "number"],
                    value=[],
                    interactive=False
                )

        gr.Markdown("---")

        # Bottom: Coach Meta-Question Box & Final Report
        with gr.Row():
            with gr.Column(scale=6):
                gr.Markdown("### 🤖 Coach / Meta-Question Box")
                coach_input = gr.Textbox(
                    placeholder="e.g., 'How am I doing so far?' or 'What is my weakest area?'",
                    label="Ask the Coach about your progress"
                )
                coach_btn = gr.Button("Ask Coach")
                coach_output = gr.Markdown("")

            with gr.Column(scale=6):
                gr.Markdown("### 🏁 Session Completion & Final Report")
                report_btn = gr.Button("Generate Final Report", variant="stop")
                report_output = gr.Markdown("")

        # Attach Event Listeners (Added answer_input to outputs to clear it)
        submit_btn.click(
            fn=submit_answer,
            inputs=[answer_input, state],
            outputs=[feedback_output, scorecard_table, current_q_box, answer_input, state]
        )

        coach_btn.click(
            fn=ask_coach,
            inputs=[coach_input, state],
            outputs=[coach_output]
        )

        report_btn.click(
            fn=generate_report,
            inputs=[state],
            outputs=[report_output]
        )

    return demo

if __name__ == "__main__":
    app = build_ui()
    app.launch(theme=gr.themes.Soft())