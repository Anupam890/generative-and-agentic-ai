from langchain import hub
from langchain.agents import create_react_agent,AgentExecutor
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools.tools import web_scrape,web_search
import os
from dotenv import load_dotenv

#load environment variables
load_dotenv()

llm_model = ChatMistralAI(api_key=os.getenv("MISTRAL_API_KEY"),model="mistral-7b-instruct-v0.1.Q4_0.gguf",temperature=0)


#first agent

def build_serach_agent():
    prompt = hub.pull("hwchase17/react")
    agent = create_react_agent(llm=llm_model,tools=[web_search],prompt=prompt)
    return AgentExecutor
