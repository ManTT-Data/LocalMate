"""Supabase client for database and auth operations."""

from supabase import Client, create_client

from app.core.config import settings

# Create Supabase client with service role key for server-side operations
supabase: Client = create_client(
    settings.supabase_url,
    settings.supabase_service_role_key,
)


def get_supabase() -> Client:
    """Get Supabase client instance."""
    return supabase
