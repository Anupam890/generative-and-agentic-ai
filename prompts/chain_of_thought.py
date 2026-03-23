from openai import OpenAI
import json

# Initialize client
client = OpenAI(
    api_key="AIzaSyAwTbeOvZPE0vpgpDIvEgZBlc_KvMmCzok",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# System prompt for the assistant
SYSTEM_PROMPT = """
You are an expert AI Assistant in resolving user queries using chain of thought.
you work on START, PLAN and OUTPUT strategy.
you need to first plan what needs to be done. the PLAN can be in multiple steps.
once you think enough PLAN has been done, finally give the OUTPUT.

Rules:
- strictly follow the given JSON output format
- only run one step at a time.
- the sequence of the steps is start (where user gives an input), plan (where you plan the steps needed to solve the problem), output (where you give the final answer)

Output Format:
{
"step": "START/PLAN/OUTPUT",
"content": "your content here"
}

Examples:
START: Hey, Can you Solve 3+5*2/10 for me?
PLAN: {"step": "PLAN", "content": "First, I will solve the multiplication 5*2=10. Then I will solve the division 10/10=1. Finally, I will add 3+1=4"}
OUTPUT: {"step": "OUTPUT", "content": "The final answer is 4"}
"""

# Message history for context
message_history = [
    {"role": "system", "content": SYSTEM_PROMPT},
]

# Take user input
user_query = input("Enter your query: ")
message_history.append({"role": "user", "content": user_query})

# Conversation loop
while True:
    response = client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=message_history,
        response_format={"type": "json_object"}  # ✅ Correct format
    )

    # Get assistant's response
    raw_response = response.choices[0].message.content
    parsed_response = json.loads(raw_response)

    # Append assistant response to history
    message_history.append({"role": "assistant", "content": raw_response})

    # Handle steps
    step = parsed_response.get("step")
    content = parsed_response.get("content")

    if step == "START":
        print("🔥", content)
        continue
    elif step == "PLAN":
        print("📝", content)
        continue
    elif step == "OUTPUT":
        print("🎉", content)
        break

"""
Enter your query: write a code to add two numbers in js
🔥 write a code to add two numbers in js
📝 1. Define a JavaScript function that takes two parameters (numbers). 2. Inside the function, return the sum of the two parameters. 3. Provide an example of how to call this function and display the result.
🎉 ```javascript
function addNumbers(num1, num2) {
  return num1 + num2;
}

// Example usage:
let number1 = 5;
let number2 = 10;
let sum = addNumbers(number1, number2);

console.log("The sum is: " + sum); // Output: The sum is: 15

// Another example:
console.log("20 + 7 is: " + addNumbers(20, 7)); // Output: 20 + 7 is: 27
"""
