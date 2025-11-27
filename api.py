from fastapi import FastAPI
from pydantic import BaseModel
from chatbot_core import route_message
import uvicorn

app = FastAPI(title="Upgraded NLP Chatbot API")

@app.get("/")
def root():
    return {"message": "Chatbot API is running!"}

class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str

@app.post("/chat")
def chat(req: ChatRequest):

    res = route_message(req.session_id, req.message)
    return res

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
