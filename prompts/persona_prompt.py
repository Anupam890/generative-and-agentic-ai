# Persona Based Prompting 
from openai import OpenAI

client = OpenAI(
    api_key="AIzaSyAwTbeOvZPE0vpgpDIvEgZBlc_KvMmCzok",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# Persona Based Prompting : Here we define a specific persona for the model to follow.
SYSTEM_PROMPT = """
You are an AI persona Assistant named ANUPAM.
who is a tech enthusiast, loves to code, and is always eager to help with programming-related queries and a Software Engineer.
He's a 22 Years old tech Enthusiast.
Your Main tech Stack is Python , Javascript. you are learning GenAI these Days

Examples:
Q: Hey
A: Hi there! I'm Anupam, your friendly coding assistant. How can I help you today?




"""

response = client.chat.completions.create(
    model="gemini-2.5-flash",
    # response_format={"type": "json_object"},
    messages=[
        # system prompt to set behavior of the LLM(ex: This is a maths assistant etc)
        {"role": "system", "content": SYSTEM_PROMPT},
        
        {
            "role": "user",
            "content": "Who are You?",
        }
    ]
)

print(response.choices[0].message)