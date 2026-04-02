import sys
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
import chat_handler
import database as db

app = FastAPI(title="Dearly Premium API", description="Gifting AI with Supabase metrics & rating.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    session_id: str
    message: str
    location: Optional[str] = None
    is_regeneration: Optional[bool] = False

class NoteRequest(BaseModel):
    session_id: str
    idea_title: str
    idea_reasoning: str
    recipient_name: Optional[str] = "them"

class NoteCopiedRequest(BaseModel):
    session_id: str
    idea_title: str
    user_location: Optional[str] = None

class RatingRequest(BaseModel):
    session_id: str
    idea_title: str
    rating: int  # 1 to 5
    feedback: Optional[str] = None

class ClearSessionRequest(BaseModel):
    session_id: str


@app.post("/api/chat")
def chat(req: ChatRequest):
    return chat_handler.dearly_chat(req.session_id, req.message, req.location, req.is_regeneration)

@app.post("/api/note")
def generate_note(req: NoteRequest):
    return chat_handler.generate_note_for_idea(
        req.session_id, req.idea_title, req.idea_reasoning, req.recipient_name
    )

@app.post("/api/metrics/note-copied")
def note_copied(req: NoteCopiedRequest):
    success = db.save_note_copy(req.session_id, req.idea_title, req.user_location)
    return {"status": "recorded" if success else "failed"}

@app.post("/api/metrics/rate")
def rate_idea(req: RatingRequest):
    if req.rating < 1 or req.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5.")
    success = db.save_rating(req.session_id, req.idea_title, req.rating, req.feedback)
    return {"status": "recorded" if success else "failed"}

@app.get("/api/admin/metrics")
def admin_metrics(api_key: str = None):
    # Dummy auth for testing purposes
    if api_key != "dearly_admin_2026":
         raise HTTPException(status_code=401, detail="Unauthorized.")
    return db.get_admin_metrics()

@app.post("/api/session/clear")
def clear_session(req: ClearSessionRequest):
    chat_handler.clear_session(req.session_id)
    return {"status": "cleared", "session_id": req.session_id}
