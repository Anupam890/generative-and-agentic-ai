import requests
import os

def get_weather(city:str):
    url = f"https://wttr.in/{city}?format=%C+%t"

    res = requests.get(url).json()
    return res

def run_command(command:str):
    cmd = os.system(command)
    return cmd