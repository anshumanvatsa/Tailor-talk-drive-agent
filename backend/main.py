import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import AIMessage, HumanMessage

from agent.graph import drive_agent
from models.schemas import ChatRequest, ChatResponse

app = FastAPI(
    title="TailorTalk Drive Agent API",
    description="Conversational AI agent for Google Drive file discovery powered by LangGraph + Groq",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    try:
        history = []
        for msg in req.history:
            if msg.role == "user":
                history.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                history.append(AIMessage(content=msg.content))

        history.append(HumanMessage(content=req.message))

        result = drive_agent.invoke(
            {
                "messages": history,
                "tools_used": [],
            }
        )

        final_message = result["messages"][-1]
        tools_used = list(set(result.get("tools_used", [])))

        return ChatResponse(
            response=final_message.content,
            tools_used=tools_used,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


@app.get("/health")
def health():
    return {"status": "ok", "agent": "tailortalk-drive-agent-v1", "model": "llama-3.3-70b-versatile"}


@app.get("/")
def root():
    return {"message": "TailorTalk Drive Agent is running. POST to /chat to start."}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)