"""
Main pipeline orchestrator
Runs full ETL: Extract → Embed → Upload
"""

import asyncio
import argparse
from pathlib import Path

from .extract_places import PlaceExtractor
from .embedding_generator import EmbeddingGenerator
from .image_embedder import ImageEmbedder
from .config import RAG_PROCESSED_DIR


class RAGPipeline:
    """Orchestrate full RAG pipeline"""
    
    def __init__(self):
        self.extractor = PlaceExtractor()
        self.text_embedder = EmbeddingGenerator()
        self.image_embedder = None  # Lazy load (GPU heavy)
    
    async def run_full_pipeline(
        self,
        include_images: bool = True,
        classify_scenes: bool = True
    ):
        """
        Run complete pipeline:
        1. Extract places from Neo4j/JSON
        2. Generate text embeddings
        3. Generate image embeddings (optional)
        4. Save all to pickle files (upload to Supabase later)
        """
        print("="*80)
        print("🚀 RAG PIPELINE - FULL EXECUTION")
        print("="*80)
        
        # Step 1: Extract places
        print("\n" + "="*80)
        print("STEP 1: Extract Places")
        print("="*80)
        places = self.extractor.extract_all()
        
        if not places:
            print("❌ No places found! Check your data sources.")
            return
        
        print(f"✅ Extracted {len(places)} places")
        
        # Save normalized
        self.extractor.save_normalized(places)
        
        # Step 2: Generate text embeddings
        print("\n" + "="*80)
        print("STEP 2: Generate Text Embeddings")
        print("="*80)
        text_embeddings = await self.text_embedder.generate_for_places(places)
        print(f"✅ Generated {len(text_embeddings)} text embeddings")
        
        # Step 3: Generate image embeddings (optional)
        if include_images:
            print("\n" + "="*80)
            print("STEP 3: Generate Image Embeddings")
            print("="*80)
            
            self.image_embedder = ImageEmbedder()
            image_embeddings = self.image_embedder.generate_for_places(
                places, 
                classify_scenes=classify_scenes
            )
            print(f"✅ Generated {len(image_embeddings)} image embeddings")
        else:
            print("\n⏭️ Skipping image embeddings")
        
        # Summary
        print("\n" + "="*80)
        print("✅ PIPELINE COMPLETE!")
        print("="*80)
        print(f"📊 Total places: {len(places)}")
        print(f"📝 Text embeddings: {len(text_embeddings)}")
        if include_images and self.image_embedder:
            print(f"🖼️ Image embeddings: {len(image_embeddings)}")
        print(f"\n💾 Output directory: {RAG_PROCESSED_DIR}")
        print("\n🎯 Next step: Upload to Supabase")
        print("   Run: python -m rag_pipeline.upload_supabase")
        
        self.extractor.close()
    
    async def run_step(self, step: str):
        """Run a single step"""
        if step == "extract":
            places = self.extractor.extract_all()
            self.extractor.save_normalized(places)
            self.extractor.close()
        
        elif step == "embed_text":
            import json
            places_file = RAG_PROCESSED_DIR / "places_normalized.json"
            with open(places_file, 'r') as f:
                places_data = json.load(f)
            
            places = [self.extractor._json_to_place_data(p) for p in places_data]
            places = [p for p in places if p]
            
            await self.text_embedder.generate_for_places(places)
        
        elif step == "embed_images":
            import json
            places_file = RAG_PROCESSED_DIR / "places_normalized.json"
            with open(places_file, 'r') as f:
                places_data = json.load(f)
            
            places = [self.extractor._json_to_place_data(p) for p in places_data]
            places = [p for p in places if p]
            
            self.image_embedder = ImageEmbedder()
            self.image_embedder.generate_for_places(places, classify_scenes=True)
        
        else:
            print(f"❌ Unknown step: {step}")
            print("Available steps: extract, embed_text, embed_images")


async def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="RAG Pipeline for Da Nang Tourism")
    parser.add_argument(
        "--step",
        choices=["full", "extract", "embed_text", "embed_images"],
        default="full",
        help="Which step to run"
    )
    parser.add_argument(
        "--no-images",
        action="store_true",
        help="Skip image embedding generation"
    )
    parser.add_argument(
        "--no-scene-classification",
        action="store_true",
        help="Skip scene classification for images (faster)"
    )
    
    args = parser.parse_args()
    
    pipeline = RAGPipeline()
    
    if args.step == "full":
        await pipeline.run_full_pipeline(
            include_images=not args.no_images,
            classify_scenes=not args.no_scene_classification
        )
    else:
        await pipeline.run_step(args.step)


if __name__ == "__main__":
    asyncio.run(main())
