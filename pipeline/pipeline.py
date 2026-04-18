from agents.agents import build_search_agent, build_reader_agent, writer_chain, critic_chain



def run_research_pipeline(topic: str) -> dict:

    state = {}

    # Step 1: Search Agent - gather research
    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages": [
            {"role": "user", "content": f"Gather comprehensive research on the following topic: {topic}"}
        ]
    })
    state["search_results"] = search_result["messages"][-1].content
    print("✅ Step 1 complete: Research gathered")

    # Step 2: Reader Agent - read and extract key information
    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": f"""You are an expert research writer. Your task is to synthesize the provided research into a comprehensive, well-structured report.

**Topic:** {topic}

**Research Data:**
{state['search_results']}

---

Write a detailed research report with the following structure:

## 1. Executive Summary
A concise overview of the key findings (2-3 sentences).

## 2. Introduction
- Background and context of the topic
- Why this topic matters
- Scope of the report

## 3. Key Findings
- Synthesize the research into clear, well-supported points
- Group related findings into sub-sections
- Back every claim with evidence from the research

## 4. Analysis & Insights
- Identify patterns and trends
- Highlight contradictions or gaps in the research
- Provide critical interpretation of the findings

## 5. Conclusion
- Summarize the most important takeaways
- Suggest areas for further research

## 6. Sources
- List all sources referenced from the research data

**Guidelines:**
- Be objective and factual
- Avoid speculation beyond what the research supports
- Use clear, professional language
- Minimum 500 words
"""
            }
        ]
    })
    state["reader_output"] = reader_result["messages"][-1].content
    print("✅ Step 2 complete: Research read and extracted")

    # Step 3: Writer Chain - synthesize into a polished report
    writer_result = writer_chain.invoke({
        "topic": topic,
        "research": state["reader_output"]
    })
    state["research_report"] = writer_result
    print("✅ Step 3 complete: Report written")

    # Step 4: Critic Agent - critique the report and give score
    critic_result = critic_chain.invoke({
        "topic": topic,
        "report": state["research_report"]
    })
    state["critic_feedback"] = critic_result
    print("✅ Step 4 complete: Report critiqued")

    return state


if __name__ == "__main__":
    topic = input("Enter a research topic: ")
    result = run_research_pipeline(topic)
