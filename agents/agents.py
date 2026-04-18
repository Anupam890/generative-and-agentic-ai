from langchain import hub
from langchain.agents import create_react_agent, AgentExecutor
from langchain_community.agent_toolkits.load_tools import get_all_tool_names
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools.tools import web_scrape, web_search
import os
from dotenv import load_dotenv

#load environment variables
load_dotenv()

llm_model = ChatMistralAI(api_key=os.getenv("MISTRAL_API_KEY"), model="mistral-small-latest", temperature=0)


#first agent

def build_search_agent():
    prompt = hub.pull("hwchase17/react")
    agent = create_react_agent(llm=llm_model, tools=[web_search], prompt=prompt)
    return AgentExecutor(agent=agent, tools=[web_search], verbose=True)

def build_reader_agent():
    prompt = hub.pull("hwchase17/react")
    agent = create_react_agent(llm=llm_model, tools=[web_scrape], prompt=prompt)
    return AgentExecutor(agent=agent, tools=[web_scrape], verbose=True)

# Writer Prompt

writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and insightful reponse."),
("human", """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

Be detailed, factual and professional."""),
])

writer_chain = writer_prompt | llm_model | StrOutputParser()

# critic Chain - tells the writer to improve the report and gives score
critic_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an expert research critic and academic reviewer with deep analytical skills. 
Your role is to rigorously evaluate research reports and provide detailed, constructive feedback.

When reviewing, assess the following dimensions:
- **Clarity & Structure**: Is the report well-organized and easy to follow?
- **Accuracy & Evidence**: Are claims well-supported with credible sources?
- **Depth & Coverage**: Does the report thoroughly explore the topic?
- **Critical Thinking**: Are multiple perspectives considered? Are limitations acknowledged?
- **Actionability**: Are conclusions meaningful and actionable?

Be specific, fair, and constructive in your critique.""",
    ),
    (
        "human",
        """Evaluate the following research report based on the topic and research provided.

**Topic:** {topic}

**Research Report:**
{report}

Provide your evaluation in the following format:
1. **Overall Assessment** (1-2 sentences summarizing the report quality)
2. **Strengths** (what the report does well)
3. **Weaknesses** (areas that need improvement)
4. **Specific Suggestions** (actionable steps to improve the report)
5. **Score** (rate the report from 1-10 with justification)""",
    ),
])

critic_chain = critic_prompt | llm_model | StrOutputParser()

