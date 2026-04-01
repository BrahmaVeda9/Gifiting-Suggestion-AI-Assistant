from database import get_supabase

# Basic Example CRUD for Users
def create_user(email: str):
    db = get_supabase()
    response = db.table("users").insert({"email": email}).execute()
    if not response.data:
        raise Exception("Failed to create user")
    return response.data[0]

def get_user_by_email(email: str):
    db = get_supabase()
    response = db.table("users").select("*").eq("email", email).execute()
    return response.data[0] if response.data else None
