from supabase import create_client, Client
import os

from dotenv import load_dotenv

load_dotenv()

url: str = os.getenv("SUPABASE_URL", "https://dummy.supabase.co")
key: str = os.getenv("SUPABASE_KEY", "dummy_key")
supabase: Client = create_client(url, key)

def get_supabase() -> Client:
    return supabase

def match_strategies(embedding: list[float], limit: int = 3):
    """
    Calls a Supabase Postgres function `match_strategies` that computes the cosine distance
    between the given embedding and the stored vector embeddings of strategies.
    """
    try:
        # We assume the user has run the setup SQL in their Supabase dashboard
        response = supabase.rpc(
            'match_strategies',
            {'query_embedding': embedding, 'match_threshold': 0.7, 'match_count': limit}
        ).execute()
        return response.data
    except Exception as e:
        print(f"Error matching strategies: {e}")
        return []
