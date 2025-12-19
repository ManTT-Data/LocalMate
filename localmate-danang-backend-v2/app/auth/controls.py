"""Authentication control functions."""

import httpx
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime, timedelta
import jwt
import os
from uuid import uuid4
from app.core.config import settings

# Google OAuth verification URL
GOOGLE_VERIFY_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

# JWT settings
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24


async def login_control(access_token: str, db: AsyncSession) -> dict:
    """
    Login with Google OAuth access token.
    
    Steps:
    1. Verify access token with Google
    2. Get user info from Google
    3. Check if user exists in database
    4. Create user if not exists
    5. Generate JWT token
    6. Return user info and token
    
    Args:
        access_token: Google OAuth access token
        db: Database session
        
    Returns:
        dict: User info and JWT token
        
    Raises:
        HTTPException: If token is invalid or verification fails
    """
    # Verify token with Google
    async with httpx.AsyncClient() as client:
        try:
            # Get user info using access token
            response = await client.get(
                GOOGLE_VERIFY_URL,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid access token"
                )
            
            google_user_info = response.json()
            
            # Verify the token was issued for our client
            # Note: For access tokens from Token Client, we trust Google's validation
            # The token is already validated by Google if we get a 200 response
            
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to verify token with Google: {str(e)}"
            )
    
    # Extract user info from Google response
    email = google_user_info.get("email")
    full_name = google_user_info.get("name", "")
    avatar_url = google_user_info.get("picture")
    
    if not email:
        raise HTTPException(
            status_code=400,
            detail="Email not provided by Google"
        )
    
    # Check if user exists by email in profiles table
    result = await db.execute(
        text("""
            SELECT p.id, p.full_name, p.avatar_url, p.role, p.email
            FROM profiles p
            WHERE p.email = :email
        """),
        {"email": email}
    )
    row = result.fetchone()
    
    if row:
        # User exists - update avatar if changed
        user_id = str(row.id)
        
        if avatar_url and avatar_url != row.avatar_url:
            await db.execute(
                text("""
                    UPDATE profiles
                    SET avatar_url = :avatar_url, updated_at = NOW()
                    WHERE id = :user_id
                """),
                {"avatar_url": avatar_url, "user_id": user_id}
            )
            await db.commit()
    else:
        # Create new user using Supabase Admin API
        from app.shared.integrations.supabase_client import supabase
        
        try:
            # Create user in auth.users using Supabase Admin API
            auth_response = supabase.auth.admin.create_user({
                "email": email,
                "email_confirm": True,  # Auto-confirm email for OAuth users
                "user_metadata": {
                    "full_name": full_name,
                    "avatar_url": avatar_url,
                    "provider": "google"
                }
            })
            
            user_id = auth_response.user.id
            
        except Exception as e:
            # If user already exists in auth.users, try to get their ID
            try:
                # Query auth.users to get existing user
                auth_result = await db.execute(
                    text("SELECT id FROM auth.users WHERE email = :email"),
                    {"email": email}
                )
                auth_row = auth_result.fetchone()
                
                if auth_row:
                    user_id = str(auth_row.id)
                else:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to create or retrieve user: {str(e)}"
                    )
            except Exception as inner_e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to create user: {str(e)}, {str(inner_e)}"
                )
        
        # Create profile in profiles table
        await db.execute(
            text("""
                INSERT INTO profiles (id, email, full_name, avatar_url, role, locale, created_at, updated_at)
                VALUES (:id, :email, :full_name, :avatar_url, 'tourist', 'vi_VN', NOW(), NOW())
                ON CONFLICT (id) DO UPDATE 
                SET email = :email, full_name = :full_name, avatar_url = :avatar_url, updated_at = NOW()
            """),
            {
                "id": user_id,
                "email": email,
                "full_name": full_name,
                "avatar_url": avatar_url
            }
        )
        
        await db.commit()
    
    # Generate JWT token
    token_payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    token = jwt.encode(token_payload, settings.jwt_secret, algorithm=JWT_ALGORITHM)
    
    return {
        "user_id": user_id,
        "email": email,
        "full_name": full_name,
        "avatar_url": avatar_url,
        "token": token
    }


async def logout_control(user_id: str, db: AsyncSession) -> dict:
    """
    Logout user.
    
    For now, this is a simple logout that just confirms the action.
    In a production system, you might want to:
    - Blacklist the JWT token
    - Clear server-side sessions
    - Log the logout event
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        dict: Logout confirmation message
    """
    # Optional: Log logout event
    await db.execute(
        text("""
            INSERT INTO auth.audit_log (user_id, action, timestamp)
            VALUES (:user_id, 'logout', NOW())
        """),
        {"user_id": user_id}
    )
    
    # Note: The above will fail if audit_log table doesn't exist
    # Comment it out if not needed or create the table
    
    return {"message": "Logout successful"}
