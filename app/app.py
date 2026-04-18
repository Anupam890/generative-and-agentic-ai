import time
import os
import sys
import json
import streamlit as st
from datetime import datetime

# Add project root to path so imports work when Streamlit runs app/app.py directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agents.agents import (
    build_search_agent,
    build_reader_agent,
    build_writer_chain,
    build_revision_chain,
    build_critic_chain,
    build_fact_checker_chain,
    build_comparison_chain,
    build_graph_data_chain,
    parse_critic_score,
    AVAILABLE_MODELS,
)
from charts.charts import parse_chart_data, generate_charts
from pipeline.pipeline import (
    save_to_history,
    load_history,
    export_report_markdown,
    export_report_html,
    export_report_pdf,
    export_report_docx,
    validate_api_keys,
)

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResearchMind AI",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: #080810;
    color: #dddcec;
    font-family: 'DM Mono', monospace;
}
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] {
    background: #0d0d1a !important;
    border-right: 1px solid #1a1a2e !important;
}
[data-testid="stSidebar"] * { color: #dddcec !important; }
h1,h2,h3,h4 { font-family: 'Syne', sans-serif !important; letter-spacing: -0.02em; }

/* ── Sidebar brand ── */
.brand {
    padding: 1.5rem 0 2rem;
    text-align: center;
}
.brand-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.4rem;
    font-weight: 800;
    background: linear-gradient(135deg, #a78bfa, #60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.brand-sub {
    font-size: 0.7rem;
    color: #555570 !important;
    margin-top: 2px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}

/* ── Agent cards ── */
.agent-card {
    background: #111120;
    border: 1px solid #1a1a2e;
    border-radius: 10px;
    padding: 0.85rem 1rem;
    margin-bottom: 0.6rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    transition: all 0.35s ease;
}
.agent-card.idle   { opacity: 0.4; }
.agent-card.active { border-color: #a78bfa; background: #14142a; box-shadow: 0 0 18px rgba(167,139,250,0.12); }
.agent-card.done   { border-color: #34d399; background: #0d1a14; }

.agent-icon { font-size: 1.3rem; }
.agent-info { flex: 1; }
.agent-name { font-family: 'Syne', sans-serif; font-weight: 700; font-size: 0.85rem; }
.agent-desc { font-size: 0.68rem; color: #555570; margin-top: 1px; }
.agent-card.active .agent-desc { color: #a78bfa; }
.agent-card.done   .agent-desc { color: #34d399; }

.dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: #222238; flex-shrink: 0;
}
.agent-card.active .dot { background: #a78bfa; animation: blink 1.1s infinite; }
.agent-card.done   .dot { background: #34d399; }

@keyframes blink {
    0%,100% { opacity:1; transform:scale(1); }
    50%      { opacity:0.3; transform:scale(1.4); }
}

/* ── Main input area ── */
.hero {
    text-align: center;
    padding: 3rem 0 2rem;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #a78bfa 0%, #60a5fa 50%, #34d399 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    margin-bottom: 0.6rem;
}
.hero-sub {
    color: #555570;
    font-size: 0.85rem;
    letter-spacing: 0.08em;
}

/* ── Run button ── */
.stButton > button {
    background: linear-gradient(135deg, #7c6af7, #4f8ef7) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 0.7rem 2.5rem !important;
    width: 100% !important;
    letter-spacing: 0.03em !important;
    transition: opacity 0.2s, transform 0.1s !important;
}
.stButton > button:hover { opacity: 0.88 !important; transform: translateY(-1px) !important; }
.stButton > button:active { transform: translateY(0) !important; }

/* ── Text input ── */
.stTextInput > div > div > input {
    background: #111120 !important;
    border: 1px solid #1a1a2e !important;
    border-radius: 10px !important;
    color: #dddcec !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.95rem !important;
    padding: 0.75rem 1rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: #a78bfa !important;
    box-shadow: 0 0 0 3px rgba(167,139,250,0.15) !important;
}
label, .stSelectbox label { color: #555570 !important; font-size: 0.75rem !important; letter-spacing: 0.08em; }

/* ── Selectbox ── */
.stSelectbox > div > div {
    background: #111120 !important;
    border: 1px solid #1a1a2e !important;
    border-radius: 10px !important;
    color: #dddcec !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #111120;
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
    border: 1px solid #1a1a2e;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #555570 !important;
    border-radius: 7px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    padding: 0.45rem 1.2rem !important;
    border: none !important;
}
.stTabs [aria-selected="true"] {
    background: #1e1e38 !important;
    color: #a78bfa !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.5rem !important; }

/* ── Output boxes ── */
.report-box {
    background: #111120;
    border: 1px solid #1a1a2e;
    border-radius: 14px;
    padding: 2rem 2.2rem;
    line-height: 1.85;
    font-size: 0.88rem;
    color: #cccbdc;
}
.critic-box {
    background: #111120;
    border: 1px solid #1a1a2e;
    border-left: 3px solid #a78bfa;
    border-radius: 14px;
    padding: 2rem 2.2rem;
    line-height: 1.85;
    font-size: 0.88rem;
    color: #cccbdc;
}
.search-box {
    background: #111120;
    border: 1px solid #1a1a2e;
    border-left: 3px solid #60a5fa;
    border-radius: 14px;
    padding: 1.5rem 2rem;
    line-height: 1.75;
    font-size: 0.82rem;
    color: #9090aa;
    max-height: 320px;
    overflow-y: auto;
}
.fact-box {
    background: #111120;
    border: 1px solid #1a1a2e;
    border-left: 3px solid #f59e0b;
    border-radius: 14px;
    padding: 2rem 2.2rem;
    line-height: 1.85;
    font-size: 0.88rem;
    color: #cccbdc;
}

/* ── Step badge ── */
.step-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: #1a1a2e;
    border: 1px solid #252540;
    border-radius: 999px;
    padding: 0.25rem 0.9rem;
    font-size: 0.72rem;
    color: #6060a0;
    margin-bottom: 1rem;
    font-family: 'Syne', sans-serif;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

/* ── Score badge ── */
.score-badge {
    display: inline-flex; align-items: center; gap: 0.5rem;
    padding: 0.5rem 1.2rem; border-radius: 999px;
    font-family: 'Syne', sans-serif; font-weight: 700; font-size: 1rem;
    margin: 0.5rem 0;
}
.score-high { background: #0d2818; border: 1px solid #34d399; color: #34d399; }
.score-mid  { background: #1a1a00; border: 1px solid #f59e0b; color: #f59e0b; }
.score-low  { background: #1a0d0d; border: 1px solid #ef4444; color: #ef4444; }

/* ── History card ── */
.history-card {
    background: #111120; border: 1px solid #1a1a2e; border-radius: 10px;
    padding: 1rem 1.2rem; margin-bottom: 0.5rem; cursor: pointer;
}
.history-card:hover { border-color: #a78bfa; }

/* ── Divider ── */
hr { border-color: #1a1a2e !important; margin: 1.5rem 0 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #0d0d1a; }
::-webkit-scrollbar-thumb { background: #252540; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)


# ── Helper: render agent cards ───────────────────────────────────────────────
AGENT_DEFS = [
    ("🔍", "Search Agent",   "Gathering research from the web"),
    ("📖", "Reader Agent",   "Extracting & structuring findings"),
    ("✍️",  "Writer Agent",   "Synthesizing the research report"),
    ("🎯", "Critic Agent",   "Reviewing & scoring the report"),
    ("🔎", "Fact Checker",   "Verifying claims against sources"),
    ("📊", "Analytics",      "Extracting charts from data"),
]


def agent_card(icon, name, desc, state="idle"):
    return f"""
    <div class="agent-card {state}">
        <span class="agent-icon">{icon}</span>
        <div class="agent-info">
            <div class="agent-name">{name}</div>
            <div class="agent-desc">{desc}</div>
        </div>
        <div class="dot"></div>
    </div>
    """


def render_agents(active=None, done=None):
    done = done or []
    html = ""
    for i, (icon, name, desc) in enumerate(AGENT_DEFS):
        if i in done:
            s = "done"
        elif i == active:
            s = "active"
        else:
            s = "idle"
        html += agent_card(icon, name, desc, s)
    agent_placeholder.markdown(html, unsafe_allow_html=True)


def score_badge_html(score: int) -> str:
    if score >= 8:
        cls = "score-high"
    elif score >= 5:
        cls = "score-mid"
    else:
        cls = "score-low"
    return f'<div class="score-badge {cls}">Score: {score}/10</div>'


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="brand">
        <div class="brand-title">🔬 ResearchMind AI</div>
        <div class="brand-sub">Multi-Agent AI Research</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### ⚙️ Configuration")

    # Model selection - grouped by provider
    model_options = list(AVAILABLE_MODELS.keys())
    model = st.selectbox(
        "Model",
        model_options,
        index=0,
        format_func=lambda m: f"{m} ({AVAILABLE_MODELS[m]})",
    )
    depth = st.selectbox("Research Depth", ["Quick", "Standard", "Deep"], index=1)
    max_revisions = st.slider("Max Critic Revisions", 1, 5, 2)
    score_threshold = st.slider("Score Threshold (stop revising)", 1, 10, 8)

    st.markdown("<hr>", unsafe_allow_html=True)

    # Mode selection
    st.markdown("#### 🔀 Mode")
    mode = st.radio("Research Mode", ["Single Topic", "Compare Topics"], horizontal=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # File upload
    st.markdown("#### 📎 Upload Source Documents")
    uploaded_files = st.file_uploader(
        "Add PDFs or text files as extra research sources",
        accept_multiple_files=True,
        type=["pdf", "txt", "md"],
    )

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("#### 🤖 Agent Pipeline")
    agent_placeholder = st.empty()
    render_agents()

    st.markdown("<hr>", unsafe_allow_html=True)

    # Research history
    st.markdown("#### 📜 Research History")
    history = load_history()
    if history:
        for i, entry in enumerate(reversed(history[-10:])):
            ts = entry.get("timestamp", "")[:16].replace("T", " ")
            score = entry.get("critic_score", "?")
            if st.button(f"📄 {entry['topic'][:30]}... ({score}/10)", key=f"hist_{i}"):
                st.session_state.results = {
                    "research_report": entry.get("report", ""),
                    "critic_feedback": entry.get("critic_feedback", ""),
                    "critic_score": entry.get("critic_score", 0),
                    "fact_check": entry.get("fact_check", ""),
                    "search_results": "",
                    "revisions": [],
                }
                st.rerun()
    else:
        st.caption("No research history yet.")

    st.markdown("""
    <div style='font-size:0.7rem; color:#333355; text-align:center; padding:1rem 0;'>
        Powered by ResearchMind AI
    </div>""", unsafe_allow_html=True)


# ── Main Area ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-title">Deep Research,<br>Fully Automated.</div>
    <div class="hero-sub">Enter a topic · AI agents search, write & critique · Get a polished report</div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 4, 1])
with col2:
    if mode == "Single Topic":
        topic = st.text_input(
            "Research topic",
            placeholder="e.g. The impact of AI on global employment markets...",
            label_visibility="collapsed",
        )
    else:
        topic = st.text_input(
            "Topics to compare (comma-separated)",
            placeholder="e.g. Solar energy, Wind energy, Nuclear energy",
            label_visibility="collapsed",
        )
    run = st.button("🚀  Run Research Pipeline")

st.markdown("<hr>", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "results" not in st.session_state:
    st.session_state.results = None


# ── Extract uploaded file text ────────────────────────────────────────────────
def extract_uploaded_text(files) -> str:
    texts = []
    for f in files:
        if f.name.endswith(".pdf"):
            try:
                from PyPDF2 import PdfReader
                reader = PdfReader(f)
                pdf_text = "\n".join(page.extract_text() or "" for page in reader.pages)
                texts.append(f"[From {f.name}]\n{pdf_text[:3000]}")
            except Exception as e:
                texts.append(f"[Failed to read {f.name}: {e}]")
        else:
            content = f.read().decode("utf-8", errors="ignore")
            texts.append(f"[From {f.name}]\n{content[:3000]}")
    return "\n\n".join(texts)


# ── Pipeline execution ────────────────────────────────────────────────────────
if run:
    if not topic.strip():
        st.warning("Please enter a research topic first.")
    else:
        # Validate API keys
        try:
            validate_api_keys(model)
        except EnvironmentError as e:
            st.error(str(e))
            st.stop()

        st.session_state.results = None
        state = {"revisions": [], "timings": {}}
        start_time = time.time()

        # Get uploaded file text
        extra_context = ""
        if uploaded_files:
            extra_context = extract_uploaded_text(uploaded_files)

        col_l, col_r = st.columns([3, 2])
        with col_l:
            output_area = st.empty()

        if mode == "Compare Topics":
            # ── COMPARISON MODE ──────────────────────────────────────────
            topics = [t.strip() for t in topic.split(",") if t.strip()]
            if len(topics) < 2:
                st.warning("Please enter at least 2 topics separated by commas.")
                st.stop()

            render_agents(active=0, done=[])
            with col_l:
                output_area.markdown(f"""
                <div class="step-badge">⟳ Step 1 — Researching {len(topics)} topics</div>
                <div class="search-box">🔍 Searching for: <b>{', '.join(topics)}</b></div>
                """, unsafe_allow_html=True)

            per_topic = {}
            for i, t in enumerate(topics):
                search_agent = build_search_agent(model)
                search_result = search_agent.invoke({
                    "messages": [{"role": "user", "content": f"Research: {t}"}]
                })
                per_topic[t] = search_result["messages"][-1].content

            render_agents(active=2, done=[0, 1])
            with col_l:
                output_area.markdown("""
                <div class="step-badge">⟳ Step 2 — Writing comparative analysis</div>
                <div class="search-box">📊 Generating comparison report...</div>
                """, unsafe_allow_html=True)

            combined = "\n\n".join(f"=== {t} ===\n{d}" for t, d in per_topic.items())
            if extra_context:
                combined += f"\n\n=== Uploaded Documents ===\n{extra_context}"

            comparison = build_comparison_chain(model)
            report = comparison.invoke({
                "topics": ", ".join(topics),
                "research": combined,
            })

            render_agents(active=3, done=[0, 1, 2])
            with col_l:
                output_area.markdown("""
                <div class="step-badge">⟳ Step 3 — Critic reviewing</div>
                <div class="search-box">🎯 Evaluating comparison report...</div>
                """, unsafe_allow_html=True)

            critic = build_critic_chain(model)
            feedback = critic.invoke({"topic": f"Comparison: {', '.join(topics)}", "report": report})
            score = parse_critic_score(feedback)

            # Step 4: Analytics (graph extraction)
            render_agents(active=5, done=[0, 1, 2, 3])
            with col_l:
                output_area.markdown("""
                <div class="step-badge">⟳ Step 4 — Extracting analytics</div>
                <div class="search-box">📊 Detecting chartable data in report...</div>
                """, unsafe_allow_html=True)

            try:
                graph_chain = build_graph_data_chain(model)
                raw_chart_json = graph_chain.invoke({"report": report})
                chart_specs = parse_chart_data(raw_chart_json)
                chart_images = generate_charts(chart_specs)
            except Exception:
                chart_specs, chart_images = [], []

            render_agents(active=None, done=[0, 1, 2, 3, 5])
            output_area.empty()

            state["research_report"] = report
            state["critic_feedback"] = feedback
            state["critic_score"] = score
            state["search_results"] = combined
            state["chart_specs"] = chart_specs
            state["chart_images"] = chart_images
            state["timings"]["total"] = round(time.time() - start_time, 1)

        else:
            # ── SINGLE TOPIC MODE ────────────────────────────────────────
            max_search = {"Quick": 3, "Standard": 5, "Deep": 10}.get(depth, 5)

            # Step 1: Search
            render_agents(active=0, done=[])
            with col_l:
                output_area.markdown(f"""
                <div class="step-badge">⟳ Step 1 of 5</div>
                <div class="search-box">🔍 Searching the web for: <b>{topic}</b> ...</div>
                """, unsafe_allow_html=True)

            t0 = time.time()
            search_agent = build_search_agent(model)
            search_result = search_agent.invoke({
                "messages": [{"role": "user", "content": f"Gather comprehensive research on: {topic}. Find at least {max_search} diverse sources."}]
            })
            state["search_results"] = search_result["messages"][-1].content
            if extra_context:
                state["search_results"] += f"\n\n=== Uploaded Documents ===\n{extra_context}"
            state["timings"]["search"] = round(time.time() - t0, 1)

            # Step 2: Reader
            render_agents(active=1, done=[0])
            with col_l:
                output_area.markdown("""
                <div class="step-badge">⟳ Step 2 of 5</div>
                <div class="search-box">📖 Reading and extracting key information...</div>
                """, unsafe_allow_html=True)

            t0 = time.time()
            reader_agent = build_reader_agent(model)
            reader_result = reader_agent.invoke({
                "messages": [{
                    "role": "user",
                    "content": f"""Synthesize the research below into a structured report.

**Topic:** {topic}

**Research Data:**
{state['search_results']}

Structure:
## 1. Executive Summary
## 2. Introduction
## 3. Key Findings
## 4. Analysis & Insights
## 5. Conclusion
## 6. Sources

Guidelines: objective, factual, professional, minimum 500 words."""
                }]
            })
            state["reader_output"] = reader_result["messages"][-1].content
            state["timings"]["reader"] = round(time.time() - t0, 1)

            # Step 3: Writer
            render_agents(active=2, done=[0, 1])
            with col_l:
                output_area.markdown("""
                <div class="step-badge">⟳ Step 3 of 5</div>
                <div class="search-box">✍️ Writing the research report...</div>
                """, unsafe_allow_html=True)

            t0 = time.time()
            writer = build_writer_chain(model)
            report = writer.invoke({"topic": topic, "research": state["reader_output"]})
            state["research_report"] = report
            state["timings"]["writer"] = round(time.time() - t0, 1)

            # Step 4: Critic + Revision Loop
            critic = build_critic_chain(model)
            revision_chain = build_revision_chain(model)

            for rev in range(max_revisions):
                render_agents(active=3, done=[0, 1, 2])
                with col_l:
                    output_area.markdown(f"""
                    <div class="step-badge">⟳ Step 4 of 5 — Revision {rev + 1}/{max_revisions}</div>
                    <div class="search-box">🎯 Critic reviewing report (revision {rev + 1})...</div>
                    """, unsafe_allow_html=True)

                t0 = time.time()
                feedback = critic.invoke({"topic": topic, "report": state["research_report"]})
                score = parse_critic_score(feedback)

                state["revisions"].append({
                    "revision": rev + 1,
                    "score": score,
                    "feedback": feedback,
                    "time": round(time.time() - t0, 1),
                })
                state["critic_feedback"] = feedback
                state["critic_score"] = score

                if score >= score_threshold:
                    break

                if rev < max_revisions - 1:
                    with col_l:
                        output_area.markdown(f"""
                        <div class="step-badge">⟳ Step 4 of 5 — Revising</div>
                        <div class="search-box">↻ Score {score}/10 — revising report based on feedback...</div>
                        """, unsafe_allow_html=True)
                    state["research_report"] = revision_chain.invoke({
                        "topic": topic,
                        "report": state["research_report"],
                        "feedback": feedback,
                    })

            # Step 5: Fact-Checker
            render_agents(active=4, done=[0, 1, 2, 3])
            with col_l:
                output_area.markdown("""
                <div class="step-badge">⟳ Step 5 of 5</div>
                <div class="search-box">🔎 Fact-checking report against sources...</div>
                """, unsafe_allow_html=True)

            t0 = time.time()
            fact_checker = build_fact_checker_chain(model)
            fact_check = fact_checker.invoke({
                "topic": topic,
                "report": state["research_report"],
                "raw_research": state["search_results"],
            })
            state["fact_check"] = fact_check
            state["timings"]["fact_check"] = round(time.time() - t0, 1)

            # Step 6: Analytics (graph extraction)
            render_agents(active=5, done=[0, 1, 2, 3, 4])
            with col_l:
                output_area.markdown("""
                <div class="step-badge">⟳ Step 6 of 6</div>
                <div class="search-box">📊 Detecting chartable data in report...</div>
                """, unsafe_allow_html=True)

            t0 = time.time()
            try:
                graph_chain = build_graph_data_chain(model)
                raw_chart_json = graph_chain.invoke({"report": state["research_report"]})
                chart_specs = parse_chart_data(raw_chart_json)
                chart_images = generate_charts(chart_specs)
            except Exception:
                chart_specs, chart_images = [], []
            state["chart_specs"] = chart_specs
            state["chart_images"] = chart_images
            state["timings"]["analytics"] = round(time.time() - t0, 1)

            state["timings"]["total"] = round(time.time() - start_time, 1)

        # ── All done ──────────────────────────────────────────────────────
        render_agents(active=None, done=list(range(len(AGENT_DEFS))))
        output_area.empty()

        st.session_state.results = state

        # Save to history
        save_to_history(topic, state)

        # Show completion
        total = state["timings"].get("total", 0)
        score = state.get("critic_score", 0)
        revs = len(state.get("revisions", []))
        st.success(f"Pipeline complete in {total}s | Final score: {score}/10 | Revisions: {revs}")


# ── Results Display ───────────────────────────────────────────────────────────
if st.session_state.results:
    results = st.session_state.results
    score = results.get("critic_score", 0)

    # Score badge
    st.markdown(score_badge_html(score), unsafe_allow_html=True)

    # Revision history summary
    revisions = results.get("revisions", [])
    if revisions:
        scores = [r["score"] for r in revisions]
        st.caption(f"Revision scores: {' → '.join(str(s) for s in scores)}")

    tabs = ["📄 Final Report", "📊 Analytics", "🎯 Critic Feedback", "🔎 Fact Check", "🔍 Raw Research", "⬇️ Export"]
    tab1, tab_analytics, tab2, tab3, tab4, tab5 = st.tabs(tabs)

    with tab1:
        st.markdown(results.get("research_report", ""), unsafe_allow_html=False)

    with tab_analytics:
        chart_images = results.get("chart_images", [])
        chart_specs = results.get("chart_specs", [])
        if chart_images:
            st.markdown(f"**{len(chart_images)} chart(s) generated from report data**")
            for title, img_bytes in chart_images:
                st.image(img_bytes, caption=title, use_container_width=True)
        elif chart_specs:
            st.info("Chart data was detected but could not be rendered. Ensure matplotlib is installed.")
        else:
            st.info("No chartable numerical data was detected in this report.")

    with tab2:
        st.markdown(f'<div class="critic-box">{results.get("critic_feedback", "")}</div>', unsafe_allow_html=True)
        # Show revision history
        if len(revisions) > 1:
            st.markdown("#### Revision History")
            for r in revisions:
                with st.expander(f"Revision {r['revision']} — Score: {r['score']}/10 ({r['time']}s)"):
                    st.markdown(r["feedback"])

    with tab3:
        fact = results.get("fact_check", "No fact-check data available.")
        st.markdown(f'<div class="fact-box">{fact}</div>', unsafe_allow_html=True)

    with tab4:
        st.markdown(
            f'<div class="search-box">{results.get("search_results", "")}</div>',
            unsafe_allow_html=True,
        )

    with tab5:
        st.markdown("#### Download Report")
        report_text = results.get("research_report", "")
        report_topic = topic if 'topic' in dir() else "Research Report"

        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a:
            st.download_button(
                "📝 Markdown (.md)",
                data=report_text,
                file_name="research_report.md",
                mime="text/markdown",
            )
        with col_b:
            try:
                import markdown
                html_content = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
                <title>Research Report</title>
                <style>body{{font-family:Georgia,serif;max-width:800px;margin:2rem auto;padding:0 1rem;line-height:1.8;}}</style>
                </head><body>{markdown.markdown(report_text)}</body></html>"""
                st.download_button(
                    "🌐 HTML",
                    data=html_content,
                    file_name="research_report.html",
                    mime="text/html",
                )
            except ImportError:
                st.caption("Install `markdown` for HTML export")

        with col_c:
            try:
                import io as _io
                import tempfile
                from fpdf import FPDF
                pdf = FPDF()
                pdf.add_page()
                pdf.set_auto_page_break(auto=True, margin=15)
                pdf.set_font("Helvetica", "", 10)
                for line in report_text.split("\n"):
                    if line.startswith("## "):
                        pdf.set_font("Helvetica", "B", 13)
                        pdf.cell(0, 8, line.replace("## ", ""), new_x="LMARGIN", new_y="NEXT")
                        pdf.set_font("Helvetica", "", 10)
                    elif line.startswith("# "):
                        pdf.set_font("Helvetica", "B", 15)
                        pdf.cell(0, 10, line.replace("# ", ""), new_x="LMARGIN", new_y="NEXT")
                        pdf.set_font("Helvetica", "", 10)
                    elif line.strip():
                        pdf.multi_cell(0, 6, line)
                    else:
                        pdf.ln(3)

                # Embed chart images into PDF
                pdf_chart_images = results.get("chart_images", [])
                if pdf_chart_images:
                    pdf.add_page()
                    pdf.set_font("Helvetica", "B", 14)
                    pdf.cell(0, 10, "Analytics & Charts", new_x="LMARGIN", new_y="NEXT")
                    pdf.ln(4)
                    for chart_title, chart_bytes in pdf_chart_images:
                        tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
                        try:
                            tmp.write(chart_bytes)
                            tmp.close()
                            pdf.set_font("Helvetica", "B", 11)
                            pdf.cell(0, 8, chart_title, new_x="LMARGIN", new_y="NEXT")
                            pdf.image(tmp.name, w=180)
                            pdf.ln(6)
                        finally:
                            os.unlink(tmp.name)

                st.download_button(
                    "📕 PDF (with charts)" if pdf_chart_images else "📕 PDF",
                    data=bytes(pdf.output()),
                    file_name="research_report.pdf",
                    mime="application/pdf",
                )
            except ImportError:
                st.caption("Install `fpdf2` for PDF export")

        with col_d:
            try:
                from docx import Document
                import io
                doc = Document()
                doc.add_heading("Research Report", level=0)
                for line in report_text.split("\n"):
                    if line.startswith("## "):
                        doc.add_heading(line.replace("## ", ""), level=2)
                    elif line.startswith("# "):
                        doc.add_heading(line.replace("# ", ""), level=1)
                    elif line.startswith("- "):
                        doc.add_paragraph(line[2:], style="List Bullet")
                    elif line.strip():
                        doc.add_paragraph(line)
                buf = io.BytesIO()
                doc.save(buf)
                st.download_button(
                    "📘 Word (.docx)",
                    data=buf.getvalue(),
                    file_name="research_report.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            except ImportError:
                st.caption("Install `python-docx` for Word export")

    # Timing breakdown
    timings = results.get("timings", {})
    if timings:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.caption(
            " | ".join(f"{k}: {v}s" for k, v in timings.items())
        )
