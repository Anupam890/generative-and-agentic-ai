from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os
from dotenv import load_dotenv

# loading environment variables 
load_dotenv()

# website fetching tool
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool("web_search")
def web_search(query:str)->str:
    """Search the web for recent and reliable information on a topic. Returns title, url, snippets."""
    try:
        results = tavily.search(query=query,max_results=5)
        
        out = []
        
        for r in results['results']:
            out.append(
                f'Title: {r["title"]}\nURL: {r["url"]}\nSnippet: {r["content"]:300}\n'
            )
        
        return "\n--------\n".join(out)
    except Exception as e:
        return f"An error occurred while fetching search results: {str(e)}"
    
@tool("web_scrape")
def web_scrape(url:str)->str:
    """Scrapes the content of a webpage and returns the content."""
    try:
        response = requests.get(url,timeout=8,headers={"User-Agent":"Mozilla/5.0"})
        soup = BeautifulSoup(response.text,"html.parser")
        for tag in soup(["script","style","nav","footer"]):
            tag.decompose()
        return soup.get_text(separator=" ",strip=True)[:3000]
    except Exception as e:
        return f"An error occurred while scraping the webpage: {str(e)}"