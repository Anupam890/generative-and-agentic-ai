from langgraph.prebuilt import create_react_agent
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools.tools import web_scrape, web_search
import os
import re
from dotenv import load_dotenv

load_dotenv()

# ── Model Registry ────────────────────────────────────────────────────────────
AVAILABLE_MODELS = {
    "mistral-small-latest": "Mistral",
    "mistral-medium-latest": "Mistral",
    "mistral-large-latest": "Mistral",
    "gpt-4o": "OpenAI",
    "gpt-4o-mini": "OpenAI",
    "gpt-4-turbo": "OpenAI",
    "gemini-1.5-flash": "Google",
    "gemini-1.5-pro": "Google",
}


def get_llm(model_name: str = "mistral-small-latest", temperature: float = 0):
    """Create an LLM instance based on model name. Supports Mistral, OpenAI, Google."""
    provider = AVAILABLE_MODELS.get(model_name, "Mistral")

    if provider == "OpenAI":
        from langchain_openai import ChatOpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set in .env for OpenAI models")
        return ChatOpenAI(api_key=api_key, model=model_name, temperature=temperature)

    elif provider == "Google":
        from langchain_google_genai import ChatGoogleGenerativeAI
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not set in .env for Google models")
        return ChatGoogleGenerativeAI(
            google_api_key=api_key, model=model_name, temperature=temperature
        )

    else:  # Default: Mistral
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError("MISTRAL_API_KEY not set in .env for Mistral models")
        return ChatMistralAI(
            api_key=api_key, model=model_name, temperature=temperature
        )


# ── Default LLM (backward compat) ────────────────────────────────────────────
llm_model = get_llm()


# ── Agent Builders ────────────────────────────────────────────────────────────
def build_search_agent(model_name: str = "mistral-small-latest"):
    llm = get_llm(model_name)
    return create_react_agent(model=llm, tools=[web_search])


def build_reader_agent(model_name: str = "mistral-small-latest"):
    llm = get_llm(model_name)
    return create_react_agent(model=llm, tools=[web_scrape])


# ── Writer Chain ──────────────────────────────────────────────────────────────
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert research writer. Write clear, structured and insightful reports.
Always include inline citations like [1], [2] linking to the sources listed at the end."""),
    ("human", """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points with inline citations)
- Analysis & Insights
- Conclusion
- Sources (numbered list of all URLs found in the research)

Be detailed, factual and professional. Minimum 600 words."""),
])

# ── Writer Revision Chain (takes critic feedback and improves) ────────────────
revision_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert research writer revising a report based on critic feedback.
Maintain inline citations [1], [2] and improve based on the specific suggestions."""),
    ("human", """Revise the research report below based on the critic's feedback.

Topic: {topic}

Original Report:
{report}

Critic Feedback:
{feedback}

Improve the report addressing every point in the critic's feedback.
Maintain the same structure but enhance clarity, depth, and accuracy.
Return the complete revised report."""),
])

# ── Critic Chain ──────────────────────────────────────────────────────────────
critic_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert research critic and academic reviewer with deep analytical skills.
Your role is to rigorously evaluate research reports and provide detailed, constructive feedback.

When reviewing, assess the following dimensions:
- **Clarity & Structure**: Is the report well-organized and easy to follow?
- **Accuracy & Evidence**: Are claims well-supported with credible sources?
- **Depth & Coverage**: Does the report thoroughly explore the topic?
- **Critical Thinking**: Are multiple perspectives considered? Are limitations acknowledged?
- **Actionability**: Are conclusions meaningful and actionable?

IMPORTANT: You MUST end your review with exactly this format on the last line:
**Score: X/10**
where X is the numeric score. This is required for automated parsing."""),
    ("human", """Evaluate the following research report based on the topic and research provided.

**Topic:** {topic}

**Research Report:**
{report}

Provide your evaluation in the following format:
1. **Overall Assessment** (1-2 sentences summarizing the report quality)
2. **Strengths** (what the report does well)
3. **Weaknesses** (areas that need improvement)
4. **Specific Suggestions** (actionable steps to improve the report)
5. **Score: X/10** (rate the report from 1-10 with justification)"""),
])

# ── Fact-Checker Chain ────────────────────────────────────────────────────────
fact_checker_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a meticulous fact-checker. Your job is to cross-reference key claims
in a research report against the raw research data and flag any issues."""),
    ("human", """Fact-check the following research report against the raw research data.

**Topic:** {topic}

**Research Report:**
{report}

**Raw Research Data:**
{raw_research}

For each major claim in the report:
1. **Verified Claims**: Claims that are directly supported by the research data.
2. **Unverified Claims**: Claims that cannot be confirmed from the provided data.
3. **Contradictions**: Any claims that conflict with the research data.
4. **Missing Context**: Important information from the research data that was omitted.

End with a **Reliability Score: X/10** based on how well-supported the report is."""),
])

# ── Comparison Chain (for multi-topic mode) ───────────────────────────────────
comparison_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert analyst who specializes in comparative research.
Write balanced, well-structured comparisons with inline citations."""),
    ("human", """Write a detailed comparative analysis of the following topics.

Topics: {topics}

Research Data for each topic:
{research}

Structure the comparison as:
- Introduction (what is being compared and why)
- Individual Overviews (brief summary of each topic)
- Comparative Analysis (side-by-side comparison across key dimensions)
- Strengths & Weaknesses of Each
- Conclusion & Recommendation
- Sources

Be balanced, factual, and professional. Minimum 600 words."""),
])


def build_writer_chain(model_name: str = "mistral-small-latest"):
    llm = get_llm(model_name)
    return writer_prompt | llm | StrOutputParser()


def build_revision_chain(model_name: str = "mistral-small-latest"):
    llm = get_llm(model_name)
    return revision_prompt | llm | StrOutputParser()


def build_critic_chain(model_name: str = "mistral-small-latest"):
    llm = get_llm(model_name)
    return critic_prompt | llm | StrOutputParser()


def build_fact_checker_chain(model_name: str = "mistral-small-latest"):
    llm = get_llm(model_name)
    return fact_checker_prompt | llm | StrOutputParser()


def build_comparison_chain(model_name: str = "mistral-small-latest"):
    llm = get_llm(model_name)
    return comparison_prompt | llm | StrOutputParser()


def parse_critic_score(critic_text: str) -> int:
    """Extract the numeric score from critic feedback. Returns 0 if not found."""
    match = re.search(r'\*?\*?Score:?\s*(\d+)\s*/\s*10\*?\*?', critic_text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return 0


# ── Backward-compatible global chains (use default Mistral model) ─────────────
writer_chain = writer_prompt | llm_model | StrOutputParser()
critic_chain = critic_prompt | llm_model | StrOutputParser()
