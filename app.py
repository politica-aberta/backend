from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Depends, Response

from pydantic import BaseModel
from typing import List, Optional
from supabase import create_client


from config import initialize_indexes
from processing import process_chat, process_multi_party_chat
import json
from constants import SUPABASE_URL, SUPABASE_ANON_KEY
import nest_asyncio

supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


@asynccontextmanager
async def lifespan(app: FastAPI):
    nest_asyncio.apply()
    initialize_indexes()
    yield


app = FastAPI(lifespan=lifespan)


class PreviousMessage(BaseModel):
    role: str
    message: str
    references: Optional[List[dict]] = None


class ChatRequest(BaseModel):
    message: str
    previous_messages: List[PreviousMessage]
    infer_chat_mode: bool


class StreamChatRequest(BaseModel):
    political_party: str
    chat: str
    previous_messages: List[str]
    infer_chat_mode: bool


async def require_auth(request: Request):
    json_request = await request.json()
    token = json_request.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="No token provided")
    try:
        user = supabase.auth.get_user(token)
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.post("/multi-chat")
async def multi_chat(request: ChatRequest, user: dict = Depends(require_auth)):

    answer, references = await process_multi_party_chat(
        None, request.message, request.previous_messages, request.infer_chat_mode
    )
    return {"references": references, "message": answer}


@app.post("/chat")
async def chat(request: ChatRequest, user: dict = Depends(require_auth)):
    if not request.party or type(request.party) is not str:
        raise HTTPException(status_code=400, detail="Choose a party")

    answer, references = process_chat(
        request.party,
        request.message,
        request.previous_messages,
        request.infer_chat_mode,
    )

    return {"references": references, "message": answer}


@app.post("/stream-chat")
async def stream_chat(request: StreamChatRequest):
    answer, references = process_chat(
        request.political_party,
        request.chat,
        request.previous_messages,
        request.infer_chat_mode,
        stream=True,
    )

    def generate_stream_chat_response(coordinates, answer):
        yield '{"references":' + json.dumps(coordinates) + ',"message":"'
        for part in answer:
            yield part.replace('"', '\\"')
        yield '"}'

    return Response(
        content=generate_stream_chat_response(references, answer),
        media_type="application/json",
    )


@app.get("/health")
def health():
    return {"status": "OK"}
