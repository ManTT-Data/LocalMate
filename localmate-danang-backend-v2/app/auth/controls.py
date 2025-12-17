"""Authentication control functions."""

import httpx
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime, timedelta
import jwt
import os
from uuid import uuid4

# Google OAuth verification URL
GOOGLE_VERIFY_URL = "https://www.googleapis.com/oauth2/v3/userinfo?access_token="

# JWT settings (should be in environment variables)
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
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
            response = await client.get(f"{GOOGLE_VERIFY_URL}{access_token}")
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid access token"
                )
            
            google_user_info = response.json()
            
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
    
    # Check if user exists
    result = await db.execute(
        text("""
            SELECT id, full_name, avatar_url, role
            FROM profiles
            WHERE id = (
                SELECT id FROM auth.users WHERE email = :email
            )
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
        # Create new user
        user_id = str(uuid4())
        
        # Create auth.users entry (assuming Supabase-like schema)
        await db.execute(
            text("""
                INSERT INTO auth.users (id, email, created_at)
                VALUES (:id, :email, NOW())
                ON CONFLICT (email) DO UPDATE SET email = :email
                RETURNING id
            """),
            {"id": user_id, "email": email}
        )
        
        # Create profile
        await db.execute(
            text("""
                INSERT INTO profiles (id, full_name, avatar_url, role, locale, created_at, updated_at)
                VALUES (:id, :full_name, :avatar_url, 'tourist', 'vi_VN', NOW(), NOW())
            """),
            {
                "id": user_id,
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
    token = jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
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
