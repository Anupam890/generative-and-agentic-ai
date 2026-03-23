from openai import OpenAI

client = OpenAI(
    api_key="AIzaSyAwTbeOvZPE0vpgpDIvEgZBlc_KvMmCzok",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# Few-shot prompting : Directly giving the instructions to the model with few examples
# in Real world applications, this is the most commonly used prompting technique 
# we give ample amount of examples to the model to make it understand the task
# We can get the output in a structured format like JSON, XML etc
SYSTEM_PROMPT = """Your job is to assist users with their coding questions. do not answer any other questions, if they ask anything else, respond with 'I am a coding assistant and can only help with coding questions.

Rules:
- Strictly follow the output format mentioned in the examples

output Format:
{{
"code": "your generated code",
"isCodingQuestion": true/false
}}

Examples:
Question: can you tell me a joke?
Answer: {
"isCodingQuestion": false,
"code": "null"
}

Question: write a code to add two numbers in python
Answer: {
"isCodingQuestion": true,
"code": "def add(a, b):\n    return a + b"
}

"""

response = client.chat.completions.create(
    model="gemini-2.5-flash",
    messages=[
        # system prompt to set behavior of the LLM(ex: This is a maths assistant etc)
        {"role": "system", "content": SYSTEM_PROMPT},
        
        {
            "role": "user",
            "content": "wite a code to add two numbers in javascript",
        }
    ]
)

print(response.choices[0].message)