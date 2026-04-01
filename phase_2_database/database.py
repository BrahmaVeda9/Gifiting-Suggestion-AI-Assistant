import os
from supabase import create_client, Client

from dotenv import load_dotenv

load_dotenv()

url: str = os.getenv("SUPABASE_URL", "https://dummy.supabase.co")
key: str = os.getenv("SUPABASE_KEY", "dummy_key")

supabase: Client = create_client(url, key)

def get_supabase() -> Client:
    return supabase
