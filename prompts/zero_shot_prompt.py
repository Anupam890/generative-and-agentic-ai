from openai import OpenAI

client = OpenAI(
    api_key="AIzaSyAwTbeOvZPE0vpgpDIvEgZBlc_KvMmCzok",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# Zero-shot prompting : Directly giving the instructions to the model without any examples
SYSTEM_PROMPT = "Your job is to assist users with their coding questions. do not answer any other questions, if they ask anything else, respond with 'I am a coding assistant and can only help with coding questions.'"

response = client.chat.completions.create(
    model="gemini-2.5-flash",
    messages=[
        # system prompt to set behavior of the LLM(ex: This is a maths assistant etc)
        {"role": "system", "content": SYSTEM_PROMPT},
        
        {
            "role": "user",
            "content": "Tell me a joke.",
        }
    ]
)

print(response.choices[0].message)