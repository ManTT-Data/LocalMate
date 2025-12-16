"""SigLIP Image Embedding Client - Local model for image embeddings.

Uses open_clip with ViT-B-16-SigLIP model for generating 768-dim image embeddings.
Model is loaded once at startup and reused for all requests.
"""

import io
from typing import Optional
import numpy as np
from PIL import Image


class SigLIPClient:
    """
    Local SigLIP model client for image embeddings.
    
    Model: ViT-B-16-SigLIP (pretrained on WebLI)
    Output: 768-dimensional normalized embedding vector
    """
    
    _instance: Optional["SigLIPClient"] = None
    _initialized: bool = False
    
    def __new__(cls):
        """Singleton pattern - only one model instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize SigLIP model (only once)."""
        if SigLIPClient._initialized:
            return
        
        self.model = None
        self.preprocess = None
        self.device = None
        self._load_model()
        SigLIPClient._initialized = True
    
    def _load_model(self):
        """Load SigLIP model."""
        try:
            import torch
            import open_clip
            
            print("🔄 Loading SigLIP model (ViT-B-16-SigLIP)...")
            
            self.model, _, self.preprocess = open_clip.create_model_and_transforms(
                "ViT-B-16-SigLIP", pretrained="webli"
            )
            self.model.eval()
            
            # Use CUDA if available, else CPU
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model.to(self.device)
            
            print(f"✅ SigLIP model loaded on {self.device}")
            
        except ImportError as e:
            print(f"⚠️ SigLIP dependencies not installed: {e}")
            print("   Install with: pip install torch open_clip_torch pillow")
            raise
        except Exception as e:
            print(f"❌ Failed to load SigLIP model: {e}")
            raise
    
    def embed_image(self, image: Image.Image) -> np.ndarray:
        """
        Generate embedding for a PIL Image.
        
        Args:
            image: PIL Image object
            
        Returns:
            Normalized 768-dim embedding vector
        """
        import torch
        
        # Ensure RGB
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Preprocess and embed
        image_tensor = self.preprocess(image).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            image_features = self.model.encode_image(image_tensor)
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        
        return image_features.cpu().numpy()[0]
    
    def embed_image_bytes(self, image_bytes: bytes) -> np.ndarray:
        """
        Generate embedding from raw image bytes.
        
        Args:
            image_bytes: Raw image bytes (JPEG, PNG, etc.)
            
        Returns:
            Normalized 768-dim embedding vector
        """
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        return self.embed_image(image)
    
    def embed_image_url(self, image_url: str) -> Optional[np.ndarray]:
        """
        Download and embed image from URL.
        
        Args:
            image_url: URL to image
            
        Returns:
            Embedding vector or None if failed
        """
        import httpx
        
        try:
            response = httpx.get(image_url, timeout=30.0)
            response.raise_for_status()
            return self.embed_image_bytes(response.content)
        except Exception as e:
            print(f"⚠️ Failed to embed image from URL: {e}")
            return None
    
    @property
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self.model is not None


# Lazy initialization - model loads on first use
_siglip_client: Optional[SigLIPClient] = None


def get_siglip_client() -> SigLIPClient:
    """Get or create SigLIP client singleton."""
    global _siglip_client
    if _siglip_client is None:
        _siglip_client = SigLIPClient()
    return _siglip_client


# For convenience: pre-initialized client (loads model on import)
# Uncomment below to load model on app startup:
# siglip_client = get_siglip_client()
