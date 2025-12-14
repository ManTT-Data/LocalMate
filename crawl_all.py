#!/usr/bin/env python3
"""
Production crawler - AUTO-LOAD all URLs from JSON
Crawls all 73 places with 30 photos + 20 reviews each
"""

from crawl_gmaps_production import *  # Import all functions
import json

def main_full_crawl():
    """Main function to crawl all places from JSON"""
    
    # Load all URLs
    with open('all_urls.json', 'r', encoding='utf-8') as f:
        all_data = json.load(f)
    
    test_urls = [(place['name'], place['url']) for place in all_data]
    
    os.makedirs(PHOTOS_BASE_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("="*80)
    print("🚀 FULL CRAWL - ALL DANANG LOCATIONS")
    print(f"📸 Target: {PHOTOS_PER_PLACE} photos per place")
    print(f"📝 Target: {REVIEWS_TO_CRAWL} reviews per place")
    print(f"📍 Total places: {len(test_urls)}")
    print(f"⏱️  Estimated time: {len(test_urls) * 3} minutes (~{len(test_urls) * 3 / 60:.1f} hours)")
    print("="*80)
    
    print(f"\n⚠️  This will take approximately {len(test_urls) * 3 / 60:.1f} hours!")
    print("Press Ctrl+C within 5 seconds to cancel...")
    time.sleep(5)
    
    all_results = []
    
    for idx, (name, url) in enumerate(test_urls, 1):
        print(f"\n{'#'*80}")
        print(f"# Progress: {idx}/{len(test_urls)} ({idx/len(test_urls)*100:.1f}%)")
        print(f"{'#'*80}")
        
        result = crawl_place_advanced(url, name, PHOTOS_BASE_DIR)
        all_results.append(result)
        
        # Save intermediate results every 10 places
        if idx % 10 == 0:
            temp_file = os.path.join(OUTPUT_DIR, f'crawl_progress_{idx}.json')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(all_results, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Progress saved: {temp_file}")
        
        # Small delay between places
        if idx < len(test_urls):
            time.sleep(3)
    
    # Save final results
    output_file = os.path.join(OUTPUT_DIR, 'advanced_crawl_results.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        results_to_save = []
        for r in all_results:
            r_copy = r.copy()
            r_copy['photos_count'] = len(r['photos'])
            r_copy['reviews_count'] = len(r['reviews'])
            r_copy['photos_sample'] = [p['filename'] for p in r['photos'][:5]]
            r_copy['reviews_sample'] = r['reviews'][:3]
            del r_copy['photos']
            results_to_save.append(r_copy)
        
        json.dump(results_to_save, f, indent=2, ensure_ascii=False)
    
    # Final summary
    print("\n" + "="*80)
    print("🎉 CRAWLING COMPLETE!")
    print("="*80)
    
    total_photos = sum(len(r['photos']) for r in all_results)
    total_reviews = sum(len(r['reviews']) for r in all_results)
    successful = sum(1 for r in all_results if r['success'])
    
    print(f"\n📊 FINAL STATISTICS:")
    print(f"   ✅ Successful: {successful}/{len(all_results)}")
    print(f"   📸 Total photos: {total_photos}")
    print(f"   📝 Total reviews: {total_reviews}")
    print(f"\n📁 Results saved to:")
    print(f"   JSON: {output_file}")
    print(f"   Photos: {PHOTOS_BASE_DIR}/")
    print("\n💡 Next step: Run merge_data.py to combine with Excel data")
    print("="*80)

if __name__ == '__main__':
    main_full_crawl()
