#!/usr/bin/env python3
"""
Merge Excel data with crawled data and restructure output
Each place gets: folder with photos/ + place_data.json
"""

import pandas as pd
import json
import os
import shutil
from pathlib import Path
import re

def slugify(text):
    """Convert text to safe filename"""
    text = re.sub(r'[^\w\s-]', '', text.lower())
    text = re.sub(r'[-\s]+', '_', text)
    return text[:50]

def load_all_excel_data(sheet_dir):
    """Load all Excel files and combine"""
    all_places = []
    excel_files = [
        '[5] Finding accommodation.xlsx',
        '[8] Food & Dining options.xlsx',
        '[9]Coffee shop in Danang.xlsx',
        '[12] Health & Fitness.xlsx',
        '[13]. Nightlife & Entertainment.xlsx'
    ]
    
    for filename in excel_files:
        filepath = os.path.join(sheet_dir, filename)
        if os.path.exists(filepath):
            print(f"📖 Reading {filename}...")
            
            # Read ALL sheets, not just first one
            xl_file = pd.ExcelFile(filepath)
            for sheet_name in xl_file.sheet_names:
                try:
                    df = pd.read_excel(filepath, sheet_name=sheet_name, header=1)
                    
                    # Convert DataFrame to list of dicts
                    for _, row in df.iterrows():
                        place_data = row.to_dict()
                        # Add source file info
                        place_data['source_file'] = filename
                        place_data['sheet'] = sheet_name
                        all_places.append(place_data)
                except Exception as e:
                    print(f"   ⚠️ Error reading {sheet_name}: {str(e)[:50]}")
                    continue
    
    print(f"✅ Loaded {len(all_places)} places from Excel")
    return all_places

def merge_and_restructure(excel_data, crawled_results_file, output_base_dir, urls_mapping_file='all_urls.json'):
    """Merge Excel data with crawled data and create per-place folders"""
    
    # Load crawled results
    with open(crawled_results_file, 'r', encoding='utf-8') as f:
        crawled_data = json.load(f)
    
    # Load URL mapping (links Excel names to crawled URLs)
    url_mapping = {}
    if os.path.exists(urls_mapping_file):
        with open(urls_mapping_file, 'r', encoding='utf-8') as f:
            urls_list = json.load(f)
            # Create mapping: URL -> Excel name
            for entry in urls_list:
                url_mapping[entry['url']] = entry['name']
        print(f"✅ Loaded {len(url_mapping)} URL mappings from {urls_mapping_file}")
    else:
        print(f"⚠️ URL mapping file not found: {urls_mapping_file}")
    
    # Create output directory
    os.makedirs(output_base_dir, exist_ok=True)
    
    # Track used slugs to avoid duplicates
    used_slugs = {}
    
    # Process each crawled place
    for crawled in crawled_data:
        place_name = crawled.get('name', 'Unknown')
        place_url = crawled.get('url', '')
        
        print(f"\n🔄 Processing: {place_name}")
        
        # Get Excel name from URL mapping
        excel_name_from_mapping = url_mapping.get(place_url, '').strip()
        
        # Find matching Excel data using the mapped name
        excel_match = None
        
        if excel_name_from_mapping:
            # Try exact match with mapped name
            for excel_place in excel_data:
                excel_name = (
                    excel_place.get('Place') or 
                    excel_place.get('Hotel Name') or
                    excel_place.get('Cafe Name') or
                    excel_place.get('Name') or
                    ''
                )
                excel_name = str(excel_name).strip()
                
                if excel_name == excel_name_from_mapping:
                    excel_match = excel_place
                    break
            
            # Try case-insensitive match
            if not excel_match:
                excel_mapping_lower = excel_name_from_mapping.lower()
                for excel_place in excel_data:
                    excel_name = (
                        excel_place.get('Place') or 
                        excel_place.get('Hotel Name') or
                        excel_place.get('Cafe Name') or
                        excel_place.get('Name') or
                        ''
                    )
                    excel_name = str(excel_name).strip()
                    
                    if excel_name.lower() == excel_mapping_lower:
                        excel_match = excel_place
                        break
        
        if not excel_match:
            print(f"   ⚠️ No Excel match found")
            print(f"      URL: {place_url[:50]}...")
            print(f"      Mapped name: {excel_name_from_mapping or 'NOT FOUND'}")
            excel_match = {}
        else:
            matched_name = (
                excel_match.get('Place') or 
                excel_match.get('Hotel Name') or
                excel_match.get('Cafe Name') or
                excel_match.get('Name') or
                'Unknown'
            )
            print(f"   ✅ Matched with Excel: {matched_name}")
        
        # Create place folder using ACTUAL crawled name for consistency
        actual_name = crawled.get('data', {}).get('name', place_name)
        base_slug = slugify(actual_name)
        
        # Handle duplicate slugs by adding counter
        if base_slug in used_slugs:
            used_slugs[base_slug] += 1
            place_slug = f"{base_slug}_{used_slugs[base_slug]}"
            print(f"   ⚠️ Duplicate slug detected, using: {place_slug}")
        else:
            place_slug = base_slug
            used_slugs[base_slug] = 0
        
        place_dir = os.path.join(output_base_dir, place_slug)
        photos_dir = os.path.join(place_dir, 'photos')
        os.makedirs(photos_dir, exist_ok=True)
        
        # Copy photos using actual slug
        old_photo_dir = f"data/photos/{place_slug}"
        if os.path.exists(old_photo_dir):
            photo_files = [f for f in os.listdir(old_photo_dir) if f.endswith('.jpg')]
            for photo_file in photo_files:
                src = os.path.join(old_photo_dir, photo_file)
                dst = os.path.join(photos_dir, photo_file)
                shutil.copy2(src, dst)
            print(f"   📸 Copied {len(photo_files)} photos")
        else:
            print(f"   ⚠️ Photo folder not found: {old_photo_dir}")
        
        # Merge data
        # Get raw Excel for proper column mapping
        raw_excel = excel_match
        
        merged_data = {
            # Excel data - map from actual Excel columns
            'excel_data': {
                # Name fields (different per file type)
                'name': (
                    raw_excel.get('Place') or 
                    raw_excel.get('Hotel Name') or 
                    raw_excel.get('Cafe Name') or
                    raw_excel.get('Name') or
                    excel_match.get('Name', place_name)
                ),
                
                # Location
                'address': raw_excel.get('Address', ''),
                
                # Price fields (different names per sheet)
                'price': (
                    raw_excel.get('Estimated Price (VND/night)') or
                    raw_excel.get('Price (VND)') or
                    raw_excel.get('Price Range (VND)') or
                    raw_excel.get('Price Range') or
                    excel_match.get('Price', '')
                ),
                
                # Description fields
                'description': (
                    raw_excel.get('Description') or
                    raw_excel.get('Key Highlights') or
                    excel_match.get('Description', '')
                ),
                
                # Specialty/Vibe fields
                'specialty': (
                    raw_excel.get('Specialty Dish') or
                    raw_excel.get('Vibe') or
                    raw_excel.get('Specialization') or
                    raw_excel.get('Suitable For') or
                    excel_match.get('Specialty', '')
                ),
                
                # Hours
                'opening_hours': raw_excel.get('Opening Hours', ''),
                
                # Metadata
                'source_file': excel_match.get('source_file', ''),
                
                # Keep raw for reference
                'raw_excel': raw_excel
            },
            
            # Crawled data (new)
            'crawled_data': {
                'name': crawled.get('data', {}).get('name', place_name),
                'rating': crawled.get('data', {}).get('rating'),
                'address': crawled.get('data', {}).get('address'),
                'coordinates': crawled.get('data', {}).get('coordinates'),
                'category': crawled.get('data', {}).get('category'),
                'phone': crawled.get('data', {}).get('phone'),
                'website': crawled.get('data', {}).get('website'),
            },
            
            # Photos
            'photos': {
                'count': crawled.get('photos_count', 0),
                'folder': 'photos/',
                'files': [f"photo_{i+1:03d}.jpg" for i in range(crawled.get('photos_count', 0))]
            },
            
            # Reviews
            'reviews': {
                'count': len(crawled.get('reviews', [])),  # Actual count
                'data': crawled.get('reviews', [])          # Full reviews, not sample
            },
            
            # Metadata
            'metadata': {
                'google_maps_url': place_url,
                'slug': place_slug,
                'crawled_at': crawled.get('crawled_at', 'unknown')
            }
        }
        
        # Save merged JSON
        json_path = os.path.join(place_dir, 'place_data.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Saved to: {place_dir}/")
    
    print(f"\n{'='*80}")
    print(f"✅ RESTRUCTURING COMPLETE")
    print(f"   Output: {output_base_dir}/")
    print(f"   Format: <place_slug>/photos/ + place_data.json")
    print('='*80)

def main():
    # Configuration
    SHEET_DIR = 'sheet'
    CRAWLED_RESULTS = 'data/crawled/advanced_crawl_results.json'
    OUTPUT_DIR = 'data/places'
    
    print("="*80)
    print("🔄 DATA MERGER & RESTRUCTURE")
    print("="*80)
    
    # Load Excel data
    excel_data = load_all_excel_data(SHEET_DIR)
    
    # Merge and restructure
    merge_and_restructure(excel_data, CRAWLED_RESULTS, OUTPUT_DIR)
    
    print("\n✅ Done! Check output in: data/places/")

if __name__ == '__main__':
    main()
