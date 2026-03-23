from google import genai
from google.genai import errors
import requests


client = genai.Client(api_key="AIzaSyBHBh_nVDhhFgt8gxQIvyo6tF7eH4R4aZQ")

def get_weather(city: str):
    url = f"https://wttr.in/{city.lower()}?format=%C+%t"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        return f"The weather in {city} is {response.text}"
    else:
        return "Something went wrong!"



print("Chatbot initialized. Type 'exit' to quit.")

while True:
    user_query = input("> ")
    
    if user_query.lower() == "exit":
        print("Goodbye!")
        break

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=user_query,

        )
        print(f"agent: {response.text}")

    except errors.ClientError as e:
        if e.status_code == 429:
            print("⚠️ Rate limit hit. Please wait a moment before asking again.")
        else:
            print(f"An error occurred: {e}")