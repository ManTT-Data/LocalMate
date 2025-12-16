"""Supabase client for database and auth operations."""

from supabase import create_client

from app.core.config import settings

# Initialize Supabase client
supabase = create_client(
    settings.supabase_url,
    settings.supabase_service_role_key,
)
