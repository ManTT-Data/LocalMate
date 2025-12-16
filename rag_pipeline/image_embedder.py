"""
Generate image embeddings using SigLIP via OpenCLIP (SOTA for zero-shot retrieval)
"""

import torch
import pickle
from PIL import Image
from pathlib import Path
from typing import List, Optional
from tqdm import tqdm
import numpy as np

import open_clip

from .models import PlaceData, ImageEmbedding
from .config import (
    IMAGE_EMBEDDING_DIM, IMAGE_BATCH_SIZE,
    PHOTOS_DIR, RAG_PROCESSED_DIR
)


class ImageEmbedder:
    """Generate SigLIP embeddings for place images using OpenCLIP"""
    
    def __init__(self, model_name: str = "ViT-B-16-SigLIP", pretrained: str = "webli"):
        print(f"🔄 Loading SigLIP model: {model_name} (pretrained: {pretrained})")
        
        # Use OpenCLIP for SigLIP
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            model_name, 
            pretrained=pretrained
        )
        self.tokenizer = open_clip.get_tokenizer(model_name)
        
        # Use GPU if available
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        self.model.eval()
        
        # Get embedding dimension
        with torch.no_grad():
            dummy_img = torch.zeros(1, 3, 224, 224).to(self.device)
            self.embedding_dim = self.model.encode_image(dummy_img).shape[-1]
        
        print(f"✅ Model loaded on {self.device}")
        print(f"📊 Embedding dimension: {self.embedding_dim}")
    
    def embed_image(self, image_path: str) -> Optional[np.ndarray]:
        """Embed a single image"""
        try:
            image = Image.open(image_path).convert('RGB')
            image_tensor = self.preprocess(image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                image_features = self.model.encode_image(image_tensor)
                # Normalize embeddings (important for cosine similarity)
                image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            
            return image_features.cpu().numpy()[0]
        except Exception as e:
            print(f"  ⚠️ Failed to embed {image_path}: {e}")
            return None
    
    def classify_scene_type(self, image_path: str) -> str:
        """
        Classify image scene using zero-shot SigLIP
        Returns: 'interior', 'exterior', 'food', 'view', 'people', 'other'
        """
        try:
            image = Image.open(image_path).convert('RGB')
            image_tensor = self.preprocess(image).unsqueeze(0).to(self.device)
            
            # Define scene types with descriptive text
            scene_labels = [
                "interior of a restaurant or cafe",
                "exterior building facade",
                "delicious food dish",
                "beautiful scenic view or landscape",
                "people dining or crowd",
                "other scene"
            ]
            
            text_tokens = self.tokenizer(scene_labels).to(self.device)
            
            with torch.no_grad():
                image_features = self.model.encode_image(image_tensor)
                text_features = self.model.encode_text(text_tokens)
                
                # Normalize
                image_features = image_features / image_features.norm(dim=-1, keepdim=True)
                text_features = text_features / text_features.norm(dim=-1, keepdim=True)
                
                # Compute similarities
                similarity = (image_features @ text_features.T).softmax(dim=-1)
            
            # Get top prediction
            top_idx = similarity.argmax().item()
            scene_map = ["interior", "exterior", "food", "view", "people", "other"]
            
            return scene_map[top_idx]
        except Exception as e:
            print(f"  ⚠️ Scene classification failed: {e}")
            return "other"
    
    def process_place_images(
        self, 
        place: PlaceData,
        classify_scenes: bool = True
    ) -> List[ImageEmbedding]:
        """
        Process all images for a single place
        Returns list of ImageEmbedding objects
        """
        embeddings = []
        
        for photo in place.photos:
            # Try multiple path patterns
            possible_paths = [
                Path(PHOTOS_DIR) / photo.path,  # vedas_kitchen/photos/photo_001.jpg
                Path(PHOTOS_DIR) / place.id / photo.filename,  # vedas_kitchen/photo_001.jpg
                Path(PHOTOS_DIR) / place.id / "photos" / photo.filename,  # vedas_kitchen/photos/photo_001.jpg
            ]
            
            photo_path = None
            for p in possible_paths:
                if p.exists():
                    photo_path = p
                    break
            
            if photo_path is None:
                continue
            
            # Embed image
            vector = self.embed_image(str(photo_path))
            if vector is None:
                continue
            
            # Classify scene
            scene_type = "other"
            if classify_scenes:
                scene_type = self.classify_scene_type(str(photo_path))
            
            embeddings.append(ImageEmbedding(
                place_id=place.id,
                image_url=str(photo.path),  # Relative path
                embedding=vector,
                scene_type=scene_type,
                metadata={
                    'place_name': place.name,
                    'photo_order': photo.order,
                    'filename': photo.filename
                }
            ))
        
        return embeddings
    
    def generate_for_places(
        self, 
        places: List[PlaceData],
        output_file: str = "image_embeddings.pkl",
        classify_scenes: bool = True,
        max_images_per_place: int = 10  # Limit for faster processing
    ) -> List[ImageEmbedding]:
        """
        Generate image embeddings for all places
        """
        all_embeddings = []
        total_photos = sum(min(p.photos_count, max_images_per_place) for p in places)
        
        print(f"\n🖼️ Processing images for {len(places)} places")
        print(f"📊 Max {max_images_per_place} images per place = ~{total_photos} total")
        print(f"🔍 Scene classification: {'Enabled' if classify_scenes else 'Disabled'}")
        
        for i, place in enumerate(tqdm(places, desc="Processing places")):
            # Limit photos per place
            if len(place.photos) > max_images_per_place:
                original_photos = place.photos
                place.photos = place.photos[:max_images_per_place]
            
            place_embeddings = self.process_place_images(place, classify_scenes)
            all_embeddings.extend(place_embeddings)
            
            # Restore original photos
            if len(place.photos) > max_images_per_place:
                place.photos = original_photos
            
            if (i + 1) % 20 == 0:
                print(f"  ✓ Processed {i + 1}/{len(places)} places, {len(all_embeddings)} images")
        
        # Save to pickle
        output_path = RAG_PROCESSED_DIR / output_file
        with open(output_path, 'wb') as f:
            pickle.dump(all_embeddings, f)
        
        print(f"\n✅ Generated {len(all_embeddings)} image embeddings")
        print(f"💾 Saved to {output_path}")
        
        # Show scene distribution
        from collections import Counter
        scene_counts = Counter(emb.scene_type for emb in all_embeddings)
        print(f"\n📊 Scene distribution:")
        for scene, count in scene_counts.most_common():
            print(f"  {scene}: {count}")
        
        return all_embeddings
    
    def embed_query_image(self, image_bytes: bytes) -> np.ndarray:
        """
        Embed a user-uploaded query image
        """
        from io import BytesIO
        
        try:
            image = Image.open(BytesIO(image_bytes)).convert('RGB')
            image_tensor = self.preprocess(image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                image_features = self.model.encode_image(image_tensor)
                image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            
            return image_features.cpu().numpy()[0]
        except Exception as e:
            print(f"❌ Query image embedding failed: {e}")
            return np.zeros(self.embedding_dim, dtype=np.float32)
    
    def load_embeddings(self, file_path: str = None) -> List[ImageEmbedding]:
        """Load embeddings from pickle file"""
        if file_path is None:
            file_path = RAG_PROCESSED_DIR / "image_embeddings.pkl"
        
        with open(file_path, 'rb') as f:
            embeddings = pickle.load(f)
        
        print(f"✅ Loaded {len(embeddings)} image embeddings from {file_path}")
        return embeddings


def main():
    """Test image embedding generation"""
    import json
    from .extract_places import PlaceExtractor
    
    # Load places
    places_file = RAG_PROCESSED_DIR / "places_normalized.json"
    if not places_file.exists():
        print("❌ Run extract_places.py first!")
        return
    
    with open(places_file, 'r', encoding='utf-8') as f:
        places_data = json.load(f)
    
    # Convert to PlaceData objects (first 3 for testing)
    extractor = PlaceExtractor()
    places = [extractor._json_to_place_data(p) for p in places_data[:3]]
    places = [p for p in places if p]
    
    print(f"📊 Testing with {len(places)} places")
    
    # Generate embeddings
    embedder = ImageEmbedder()
    embeddings = embedder.generate_for_places(
        places, 
        output_file="test_image_embeddings.pkl",
        classify_scenes=True
    )
    
    print(f"\n✅ Done! Generated {len(embeddings)} image embeddings")


if __name__ == "__main__":
    main()
