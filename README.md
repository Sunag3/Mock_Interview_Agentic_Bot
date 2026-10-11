# 🚀 InterviewIQ: AI-Driven Mock Interview Coach

InterviewIQ is an interactive, browser-based mock-interview application built using **Python**, **OpenAI API (`gpt-4o-mini`)**, and **Gradio**. It simulates a real-world interview process by combining deterministic, rule-based tool evaluation with an agentic LLM feedback system.

---

## 📌 Architecture & System Workflow

The diagram below illustrates the end-to-end data flow between the candidate, Gradio UI, rule-based tools, LLM agent, and dynamic session state.

```mermaid
graph TD
    %% Nodes & Styling
    classDef user fill:#E0F7FA,stroke:#006064,stroke-width:2px,color:#000;
    classDef ui fill:#FFF3E0,stroke:#E65100,stroke-width:2px,color:#000;
    classDef state fill:#F3E5F5,stroke:#4A148C,stroke-width:2px,color:#000;
    classDef tools fill:#E8F5E9,stroke:#1B5E20,stroke-width:2px,color:#000;
    classDef llm fill:#E1F5FE,stroke:#01579B,stroke-width:2px,color:#000;

    Candidate(("👤 Candidate")):::user

    subgraph UI ["🖥️ Gradio Browser Interface (app.py)"]
        QBox["📌 Current Question Box"]:::ui
        ABox["✍️ Candidate Answer Box"]:::ui
        Scorecard["📊 Live Scorecard Dataframe"]:::ui
        FPanel["💬 Immediate Feedback Panel"]:::ui
        CoachBox["🤖 Coach / Meta-Question Box"]:::ui
        ReportBox["🏁 Final Report Output Panel"]:::ui
    end

    subgraph Memory ["💾 Session State (Gradio State)"]
        Hist["Session History Log\n(Question, Answer, Tool Metrics)"]:::state
    end

    subgraph Tools ["🛠️ Deterministic Rule Tools (tools.py)"]
        TFiller["detect_filler_words()"]:::tools
        TStar["check_star_structure()"]:::tools
        TRel["score_relevance()"]:::tools
    end

    subgraph Agent ["🤖 Agent Orchestrator (agent.py)"]
        EvalEngine["evaluate_answer()"]:::llm
        FeedbackGen["generate_encouraging_feedback()"]:::llm
        CoachGen["answer_meta_question()"]:::llm
        ReportGen["generate_session_report()"]:::llm
        OpenAI["OpenAI GPT-4o-mini API"]:::llm
    end

    %% Workflow Connections
    Candidate -->|"1. Views Question"| QBox
    Candidate -->|"2. Enters Answer & Submits"| ABox
    
    ABox -->|"3. Trigger Processing"| EvalEngine
    
    EvalEngine -->|"4. Execute Tooling"| TFiller
    EvalEngine -->|"4. Execute Tooling"| TStar
    EvalEngine -->|"4. Execute Tooling"| TRel
    
    TFiller -->|"5. Return Filler Metrics"| EvalEngine
    TStar -->|"5. Return STAR Completeness"| EvalEngine
    TRel -->|"5. Return Keyword Score"| EvalEngine
    
    EvalEngine -->|"6. Store Metrics & Text"| Hist
    
    Hist -->|"7. Pass Context + Tool Outputs"| FeedbackGen
    FeedbackGen <-->|"8. Formulate Response"| OpenAI
    
    FeedbackGen -->|"9. Display Turn Feedback"| FPanel
    Hist -->|"10. Render Table Data"| Scorecard
    
    %% Meta-Coach & Report Workflows
    Candidate -->|"Ask Meta-Question\n(e.g., 'What is my weakest area?')"| CoachBox
    CoachBox -->|"Query Session History"| CoachGen
    CoachGen <-->|"Synthesize Context"| OpenAI
    CoachGen -->|"Display Direct Guidance"| CoachBox

    Candidate -->|"Click 'Generate Final Report'"| ReportBox
    ReportBox -->|"Aggregate All Turns"| ReportGen
    ReportGen <-->|"Generate Full Evaluation Summary"| OpenAI
    ReportGen -->|"Render Final Insights"| ReportBox
```

---

## ✨ Core Features

1. **Deterministic Evaluation Tools (`tools.py`)**:
   - **Filler Word Detection**: Analyzes linguistic fluency, total counts, density, and flags excessive filler usage (`um`, `like`, `basically`).
   - **STAR Framework Evaluator**: Verifies the presence of **Situation**, **Task**, **Action**, and **Result** components for behavioral questions.
   - **Relevance Scoring**: Performs keyword match analysis against predefined key concepts (0–100%).

2. **Stateful Agent Engine (`agent.py`)**:
   - Maintains continuous session context across turns.
   - Generates encouraging, actionable feedback for each response using `gpt-4o-mini`.
   - Supports mid-session coaching questions regarding overall performance.

3. **Interactive Gradio Dashboard (`app.py`)**:
   - **Current Question & Answer Box**: Clean response area with auto-clear upon submission.
   - **Live Scorecard**: Dynamic table updating with relevance %, STAR completeness, and filler word counts after every answer.
   - **Coach Q&A Box**: Meta-coaching portal allowing candidates to ask about weak points or overall progress.
   - **Final Report Generator**: End-of-session synthesis detailing average metrics, key strengths, primary growth areas, and actionable recommendations.

---

## 🛠️ Project Structure

```text
Mock_Interview_Agentic_Bot/
├── tools.py          # Deterministic rule-based evaluation functions
├── agent.py          # LLM orchestration, state management, and feedback generation
├── app.py            # Gradio web interface layout and event listeners
├── .env              # Environment variables (OpenAI API Key)
└── README.md         # Documentation & architecture diagram
```

---

## ⚡ Quick Start

### 1. Installation
Clone the repository and install required packages:
```bash
git clone https://github.com/your-username/InterviewIQ.git
cd InterviewIQ
pip install openai gradio python-dotenv
```

### 2. Environment Configuration
Create a `.env` file in the root directory and add your OpenAI API key:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Launch Application
Start the Gradio browser dashboard:
```bash
python app.py
```
Open your browser and navigate to the local URL (typically `http://127.0.0.1:7860`).

---

## 📜 License
This project is open-source under the [MIT License](LICENSE).
