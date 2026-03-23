from openai import OpenAI

client = OpenAI(
    api_key="AIzaSyAwTbeOvZPE0vpgpDIvEgZBlc_KvMmCzok",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

response = client.chat.completions.create(
    model="gemini-2.5-flash",
    messages=[
        # system prompt to set behavior of the LLM(ex: This is a maths assistant etc)
        {"role": "system", "content": "You are a Mathematics assistant."},
        
        {
            "role": "user",
            "content": "Explain the Pythagorean theorem with an example.",
        }
    ]
)

print(response.choices[0].message)