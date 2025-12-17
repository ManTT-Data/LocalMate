"""Upload Router - Image upload to Supabase Storage."""

import uuid
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel, Field

from app.shared.integrations.supabase_client import supabase
from app.core.config import settings


router = APIRouter(prefix="/upload", tags=["Upload"])

# Supabase Storage bucket name
BUCKET_NAME = "image"

# Allowed image types
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_SIZE_MB = 10


class UploadResponse(BaseModel):
    """Upload response model."""
    url: str = Field(..., description="Public URL of uploaded image")
    path: str = Field(..., description="Storage path")
    size: int = Field(..., description="File size in bytes")
    content_type: str = Field(..., description="MIME type")


@router.post(
    "/image",
    response_model=UploadResponse,
    summary="Upload image to storage",
    description="""
Upload an image file to Supabase Storage.

Returns a public URL that can be used with `/chat` endpoint's `image_url` parameter.

Supported formats: JPEG, PNG, WebP, GIF
Max size: 10MB
""",
)
async def upload_image(
    file: UploadFile = File(..., description="Image file to upload"),
    user_id: str = "anonymous",
) -> UploadResponse:
    """Upload image to Supabase Storage and return public URL."""
    
    # Validate content type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_TYPES)}"
        )
    
    # Read file content
    content = await file.read()
    
    # Validate size
    size = len(content)
    if size > MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {MAX_SIZE_MB}MB"
        )
    
    # Generate unique filename
    ext = file.filename.split(".")[-1] if file.filename and "." in file.filename else "jpg"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    filename = f"{user_id}/{timestamp}_{unique_id}.{ext}"
    
    try:
        # Upload to Supabase Storage
        result = supabase.storage.from_(BUCKET_NAME).upload(
            path=filename,
            file=content,
            file_options={"content-type": file.content_type}
        )
        
        # Get public URL
        public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(filename)
        
        return UploadResponse(
            url=public_url,
            path=filename,
            size=size,
            content_type=file.content_type,
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )
