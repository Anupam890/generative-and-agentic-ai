import time
import streamlit as st
from agents.agents import build_search_agent, build_reader_agent, writer_chain, critic_chain

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

/* ── Divider ── */
hr { border-color: #1a1a2e !important; margin: 1.5rem 0 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #0d0d1a; }
::-webkit-scrollbar-thumb { background: #252540; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)


# ── Helper: render agent cards ───────────────────────────────────────────────
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
    agents = [
        ("🔍", "Search Agent",  "Gathering research from the web"),
        ("📖", "Reader Agent",  "Extracting & structuring findings"),
        ("✍️",  "Writer Agent",  "Synthesizing the research report"),
        ("🎯", "Critic Agent",  "Reviewing & scoring the report"),
    ]
    html = ""
    for i, (icon, name, desc) in enumerate(agents):
        if i in done:
            s = "done"
        elif i == active:
            s = "active"
        else:
            s = "idle"
        html += agent_card(icon, name, desc, s)
    agent_placeholder.markdown(html, unsafe_allow_html=True)


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="brand">
        <div class="brand-title">🔬 ResearchMind</div>
        <div class="brand-sub">Multi-Agent AI Research</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### ⚙️ Configuration")
    model = st.selectbox("Model", ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"], label_visibility="visible")
    depth = st.selectbox("Research Depth", ["Standard", "Deep", "Quick"])
    max_revisions = st.slider("Max Critic Revisions", 1, 5, 2)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("#### 🤖 Agent Pipeline")
    agent_placeholder = st.empty()
    render_agents()

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:0.7rem; color:#333355; text-align:center; padding-bottom:1rem;'>
        Powered by LangChain · Tavily · GPT-4o
    </div>
    """, unsafe_allow_html=True)


# ── Main Area ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-title">Deep Research,<br>Fully Automated.</div>
    <div class="hero-sub">Enter a topic · AI agents search, write & critique · Get a polished report</div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 4, 1])
with col2:
    topic = st.text_input("", placeholder="e.g.  The impact of AI on global employment markets...")
    run = st.button("🚀  Run Research Pipeline")

st.markdown("<hr>", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "results" not in st.session_state:
    st.session_state.results = None


# ── Pipeline execution ────────────────────────────────────────────────────────
if run:
    if not topic.strip():
        st.warning("Please enter a research topic first.")
    else:
        st.session_state.results = None
        state = {}

        col_l, col_r = st.columns([3, 2])

        with col_l:
            output_area = st.empty()

        # ── Step 1: Search ──
        render_agents(active=0, done=[])
        with col_l:
            output_area.markdown("""
            <div class="step-badge">⟳ Step 1 of 4</div>
            <div class="search-box">🔍 Searching the web for research on: <b>{}</b> ...</div>
            """.format(topic), unsafe_allow_html=True)

        search_agent = build_search_agent()
        search_result = search_agent.invoke({
            "messages": [{"role": "user", "content": f"Gather comprehensive research on: {topic}"}]
        })
        state["search_results"] = search_result["messages"][-1].content

        # ── Step 2: Reader ──
        render_agents(active=1, done=[0])
        with col_l:
            output_area.markdown("""
            <div class="step-badge">⟳ Step 2 of 4</div>
            <div class="search-box">📖 Reading and extracting key information...</div>
            """, unsafe_allow_html=True)

        reader_agent = build_reader_agent()
        reader_result = reader_agent.invoke({
            "messages": [{
                "role": "user",
                "content": f"""You are an expert research writer. Synthesize the research below into a structured report.

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

        # ── Step 3: Writer ──
        render_agents(active=2, done=[0, 1])
        with col_l:
            output_area.markdown("""
            <div class="step-badge">⟳ Step 3 of 4</div>
            <div class="search-box">✍️ Writing the final research report...</div>
            """, unsafe_allow_html=True)

        writer_result = writer_chain.invoke({
            "topic": topic,
            "research": state["reader_output"]
        })
        state["research_report"] = writer_result

        # ── Step 4: Critic ──
        render_agents(active=3, done=[0, 1, 2])
        with col_l:
            output_area.markdown("""
            <div class="step-badge">⟳ Step 4 of 4</div>
            <div class="search-box">🎯 Critic agent reviewing the report...</div>
            """, unsafe_allow_html=True)

        critic_result = critic_chain.invoke({
            "topic": topic,
            "report": state["research_report"]
        })
        state["critic_feedback"] = critic_result

        render_agents(active=None, done=[0, 1, 2, 3])
        output_area.empty()

        st.session_state.results = state
        st.success("✅ Research pipeline complete!")


# ── Results Display ───────────────────────────────────────────────────────────
if st.session_state.results:
    results = st.session_state.results
    tab1, tab2, tab3 = st.tabs(["📄  Final Report", "🎯  Critic Feedback", "🔍  Raw Research"])

    with tab1:
        st.markdown(f'<div class="report-box">{results["research_report"]}</div>', unsafe_allow_html=True)
        st.download_button(
            label="⬇️  Download Report",
            data=results["research_report"],
            file_name="research_report.md",
            mime="text/markdown"
        )

    with tab2:
        st.markdown(f'<div class="critic-box">{results["critic_feedback"]}</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown(f'<div class="search-box">{results.get("search_results", "")}</div>', unsafe_allow_html=True)