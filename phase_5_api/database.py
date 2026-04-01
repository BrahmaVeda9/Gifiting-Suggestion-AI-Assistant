import os
import json
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

_url = os.getenv("SUPABASE_URL", "")
_key = os.getenv("SUPABASE_KEY", "")

_client = None
try:
    if _url and "dummy" not in _url:
        from supabase import create_client
        _client = create_client(_url, _key)
        print("[DB] Supabase connected.")
    else:
        print("[DB] Supabase credentials are placeholder — using JSON fallback.")
except Exception as e:
    print(f"[DB] Supabase init failed: {e}")

def _db():
    return _client

# ── Local JSON Fallback Helpers ──
METRICS_FILE = os.path.join(os.path.dirname(__file__), '..', 'metrics.json')

def _load_local():
    if os.path.exists(METRICS_FILE):
        try:
            with open(METRICS_FILE, 'r') as f:
                return json.load(f)
        except: pass
    return {"copies": [], "ratings": []}

def _save_local(data):
    with open(METRICS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# ── Note Copies ──

def save_note_copy(session_id: str, idea_title: str, user_location: str = None) -> bool:
    db = _db()
    data = {
        "session_id": session_id,
        "idea_title": idea_title,
        "user_location": user_location,
        "copied_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Try Supabase first
    if db:
        try:
            res = db.table("note_copies").insert(data).execute()
            # If the table doesn't exist, execute() often returns an error response instead of raising
            if hasattr(res, 'error') and res.error:
                 raise Exception(f"Supabase Error: {res.error}")
            return True
        except Exception as e:
            print(f"[DB] Supabase note_copy failed, falling back: {e}")
            pass # Fall back to local below
            
    # Local JSON fallback
    local = _load_local()
    local["copies"].append(data)
    _save_local(local)
    return True

# ── Ratings ──

def save_rating(session_id: str, idea_title: str, rating: int, feedback_text: str = None) -> bool:
    db = _db()
    data = {
        "session_id": session_id,
        "idea_title": idea_title,
        "rating": rating,
        "feedback_text": feedback_text,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Try Supabase first
    if db:
        try:
            res = db.table("idea_ratings").insert(data).execute()
            if hasattr(res, 'error') and res.error:
                 raise Exception(f"Supabase Error: {res.error}")
            return True
        except Exception as e:
            print(f"[DB] Supabase rating failed, falling back: {e}")
            pass # Fall back to local below
            
    # Local JSON fallback
    local = _load_local()
    local["ratings"].append(data)
    _save_local(local)
    return True

# ── Admin Metrics ──

def get_admin_metrics() -> dict:
    db = _db()
    copy_rows = []
    rating_rows = []
    
    use_local = True
    if db:
        try:
            copies = db.table("note_copies").select("*").order("copied_at", desc=True).execute()
            ratings = db.table("idea_ratings").select("*").order("created_at", desc=True).execute()
            
            if (hasattr(copies, 'error') and copies.error) or (hasattr(ratings, 'error') and ratings.error):
                 raise Exception("Supabase Table missing")

            copy_rows = copies.data or []
            rating_rows = ratings.data or []
            use_local = False
        except Exception as e:
            pass # Fall back to local

    if use_local:
        local = _load_local()
        copy_rows = local.get("copies", [])
        # rename keys to match superset schema
        for c in copy_rows:
            if "copied_at" not in c and "timestamp" in c:
                c["copied_at"] = c["timestamp"]
        copy_rows = sorted(copy_rows, key=lambda x: x.get("copied_at", ""), reverse=True)
            
        rating_rows = local.get("ratings", [])
        rating_rows = sorted(rating_rows, key=lambda x: x.get("created_at", ""), reverse=True)

    # Per-idea copy counts
    per_idea_copies = {}
    for row in copy_rows:
        t = row.get("idea_title")
        if t: per_idea_copies[t] = per_idea_copies.get(t, 0) + 1

    # Per-session copy counts
    per_session_copies = {}
    for row in copy_rows:
        s = row.get("session_id")
        if s: per_session_copies[s] = per_session_copies.get(s, 0) + 1

    # Per-idea average ratings
    per_idea_ratings = {}
    for row in rating_rows:
        t = row.get("idea_title")
        if t and "rating" in row:
            per_idea_ratings.setdefault(t, []).append(row["rating"])
    per_idea_avg = {k: round(sum(v) / len(v), 2) for k, v in per_idea_ratings.items()}

    # Rating distribution (1–5)
    rating_dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for row in rating_rows:
        if "rating" in row:
            rating_dist[row["rating"]] = rating_dist.get(row["rating"], 0) + 1

    return {
        "supabase_connected": not use_local,
        "total_note_copies": len(copy_rows),
        "total_ratings": len(rating_rows),
        "unique_sessions": len(per_session_copies),
        "per_idea_copies": per_idea_copies,
        "per_idea_avg_rating": per_idea_avg,
        "per_session_copies": per_session_copies,
        "rating_distribution": rating_dist,
        "recent_copies": copy_rows[:20],
        "recent_ratings": rating_rows[:20]
    }
