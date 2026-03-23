from fastapi import FastAPI,Body


app = FastAPI()


@app.get('/health-check')
def health_check():
    return {"response":"Hello World"}


@app.post('/chat')
def generate_chat():
    return None