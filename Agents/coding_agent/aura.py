import os
import subprocess
import requests
import json
from typing import Dict, Any, Callable
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

def get_weather(city: str) -> str:

    try:
        url = f"https://wttr.in/{city}?format=%C+%t"
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        return res.text
    except Exception as e:
        return f"Error fetching weather: {str(e)}"


def run_command(command: str) -> str:
    """Executes a system command and returns the output."""
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=15
        )
        return result.stdout if result.stdout else result.stderr
    except Exception as e:
        return f"Execution error: {str(e)}"


# Map tool names to functions
tools_map: Dict[str, Callable] = {
    "get_weather": get_weather,
    "run_command": run_command
}

# --- 2. Aura System Configuration ---

SYSTEM_PROMPT = """
You are "Aura," an elite Autonomous Coding Architect. 
You MUST respond in every turn using this JSON format:
{
  "thinking": "observation of user request",
  "planning": "step-by-step logic",
  "output": "final code or answer"
}
Rules:
1. Stay in character as a technical expert.
2. Use tools whenever necessary to provide real-time data or perform actions.
3. Ensure the final 'output' field contains the actual answer or code requested.
"""

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
CONFIG = types.GenerateContentConfig(
    system_instruction=SYSTEM_PROMPT,
    tools=[get_weather, run_command],
)


# --- 3. The Main Execution Loop ---

def run_aura():
    print("--- Aura Architect Online ---")
    chat = client.chats.create(model="gemini-2.5-flash", config=CONFIG)

    while True:
        user_input = input("\nUser > ")
        if user_input.lower() in ["exit", "quit"]:
            print("Aura Offline.")
            break

        try:
            # Send message to model
            response = chat.send_message(user_input)

            # Handle potential Tool/Function Calls
            while True:
                # Check if the model wants to call a function
                # Accessing the first part of the first candidate
                part = response.candidates[0].content.parts[0]

                if part.function_call:
                    call = part.function_call
                    print(f"  [System: Aura executing {call.name}...]")

                    # Execute local function
                    result = tools_map[call.name](**call.args)

                    # Send result back to continue the 'thought' process
                    response = chat.send_message(
                        types.Part.from_function_response(
                            name=call.name,
                            response={'result': result}
                        )
                    )
                else:
                    # No more function calls, we have the final text
                    break

            # Print the final formatted JSON
            if response.text:
                print(f"\nAura Architect:\n{response.text.strip()}")

        except Exception as e:
            print(f"\n[Error]: {e}")


if __name__ == "__main__":
    run_aura()