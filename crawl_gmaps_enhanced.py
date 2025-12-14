#!/usr/bin/env python3
"""
Enhanced Google Maps crawler with reviews and photos download
"""

from playwright.sync_api import sync_playwright
import json
import time
import re
import os
import requests
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import hashlib

# Configuration
PHOTOS_PER_PLACE = 20
REVIEWS_TO_CRAWL = 5
PHOTOS_BASE_DIR = "data/photos"
OUTPUT_DIR = "data/crawled"

def slugify(text):
    """Convert text to safe filename"""
    text = re.sub(r'[^\w\s-]', '', text.lower())
    text = re.sub(r'[-\s]+', '_', text)
    return text[:50]

def download_image(url, save_path):
    """Download image from URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return True
    except Exception as e:
        print(f"   ⚠️ Download error: {str(e)[:50]}")
    return False

def extract_coordinates_from_url(url):
    """Try to extract coordinates from Google Maps URL"""
    # Pattern 1: @lat,lng
    match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', url)
    if match:
        return float(match.group(1)), float(match.group(2))
    
    # Pattern 2: !3d and !4d
    lat_match = re.search(r'!3d(-?\d+\.\d+)', url)
    lng_match = re.search(r'!4d(-?\d+\.\d+)', url)
    if lat_match and lng_match:
        return float(lat_match.group(1)), float(lng_match.group(1))
    
    return None, None

def crawl_google_maps_enhanced(url, name_hint, photos_dir):
    """Crawl a single Google Maps URL with photos and reviews"""
    print(f"\n{'='*80}")
    print(f"🎯 Crawling: {name_hint}")
    print(f"URL: {url}")
    print('='*80)
    
    result = {
        'name': name_hint,
        'url': url,
        'data': {},
        'photos': [],
        'reviews': [],
        'success': False,
        'errors': []
    }
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            print("⏳ Loading page...")
            page.goto(url, wait_until='networkidle', timeout=30000)
            time.sleep(3)
            
            data = {}
            
            # ============ BASIC INFO ============
            
            # 1. Name
            try:
                name_elem = page.locator('h1').first
                if name_elem.count() > 0:
                    data['name'] = name_elem.inner_text()
                    print(f"✅ Name: {data['name']}")
            except Exception as e:
                result['errors'].append(f"Name: {str(e)}")
            
            # 2. Rating & Reviews Count
            try:
                # Try multiple selectors for rating
                rating_text = None
                
                # Selector 1: aria-label with stars
                rating_elem = page.locator('[role="img"][aria-label*="star"]').first
                if rating_elem.count() > 0:
                    aria_label = rating_elem.get_attribute('aria-label')
                    rating_match = re.search(r'(\d+\.?\d*)\s*star', aria_label)
                    if rating_match:
                        data['rating'] = float(rating_match.group(1))
                
                # Get reviews count from button or text
                reviews_patterns = [
                    'button:has-text("reviews")',
                    'button:has-text("review")',
                    '[aria-label*="review"]'
                ]
                
                for pattern in reviews_patterns:
                    elem = page.locator(pattern).first
                    if elem.count() > 0:
                        text = elem.inner_text()
                        # Match patterns like "1,234 reviews" or "1.2K reviews"
                        reviews_match = re.search(r'([\d,.]+[KMk]?)\s*review', text)
                        if reviews_match:
                            review_str = reviews_match.group(1).replace(',', '')
                            if 'K' in review_str or 'k' in review_str:
                                data['total_reviews'] = int(float(review_str.replace('K', '').replace('k', '')) * 1000)
                            elif 'M' in review_str:
                                data['total_reviews'] = int(float(review_str.replace('M', '')) * 1000000)
                            else:
                                data['total_reviews'] = int(review_str)
                            break
                
                if 'rating' in data:
                    reviews_info = f"{data['rating']} ⭐"
                    if 'total_reviews' in data:
                        reviews_info += f" ({data['total_reviews']} reviews)"
                    print(f"✅ Rating: {reviews_info}")
                    
            except Exception as e:
                result['errors'].append(f"Rating/Reviews: {str(e)}")
            
            # 3. Address
            try:
                address_elem = page.locator('button[data-item-id^="address"]').first
                if address_elem.count() > 0:
                    data['address'] = address_elem.inner_text().strip()
                    print(f"✅ Address: {data['address'][:60]}...")
            except Exception as e:
                result['errors'].append(f"Address: {str(e)}")
            
            # 4. Coordinates
            current_url = page.url
            lat, lng = extract_coordinates_from_url(current_url)
            if lat and lng:
                data['coordinates'] = {'lat': lat, 'lng': lng}
                print(f"✅ Coordinates: {lat}, {lng}")
            else:
                result['errors'].append("Coordinates not found")
            
            # 5. Category
            try:
                category_elem = page.locator('button[jsaction*="category"]').first
                if category_elem.count() > 0:
                    data['category'] = category_elem.inner_text()
                    print(f"✅ Category: {data['category']}")
            except Exception as e:
                pass
            
            # 6. Phone
            try:
                phone_elem = page.locator('button[data-item-id^="phone"]').first
                if phone_elem.count() > 0:
                    data['phone'] = phone_elem.inner_text().strip()
                    print(f"✅ Phone: {data['phone']}")
            except Exception as e:
                pass
            
            # 7. Website
            try:
                website_elem = page.locator('a[data-item-id^="authority"]').first
                if website_elem.count() > 0:
                    data['website'] = website_elem.get_attribute('href')
                    print(f"✅ Website: {data['website'][:50]}...")
            except Exception as e:
                pass
            
            # 8. Opening Hours
            try:
                # Click to expand hours if needed
                hours_button = page.locator('button[aria-label*="Hours"]').first
                if hours_button.count() > 0:
                    hours_text = hours_button.get_attribute('aria-label')
                    data['opening_hours_text'] = hours_text
                    print(f"✅ Hours info available")
            except Exception as e:
                pass
            
            # ============ REVIEWS ============
            print(f"\n📝 Crawling reviews...")
            reviews = []
            try:
                # Find and click Reviews tab - try multiple approaches
                clicked_reviews = False
                
                # Approach 1: Direct Reviews tab
                reviews_tab = page.locator('button[aria-label*="Reviews"], button:has-text("Reviews")').first
                if reviews_tab.count() > 0:
                    try:
                        reviews_tab.scroll_into_view_if_needed()
                        time.sleep(0.5)
                        reviews_tab.click()
                        time.sleep(2)
                        clicked_reviews = True
                    except:
                        pass
                
                # Approach 2: Scroll down to reviews section
                if not clicked_reviews:
                    for _ in range(3):
                        page.mouse.wheel(0, 300)
                        time.sleep(0.5)
                
                # Get review elements - try multiple selectors
                review_selectors = [
                    'div[data-review-id]',
                    'div[jslog*="review"]',
                    'div.jftiEf',  # Common Google Maps review class
                    'div[role="article"]'
                ]
                
                review_elements = []
                for selector in review_selectors:
                    elements = page.locator(selector).all()
                    if len(elements) > 0:
                        review_elements = elements[:REVIEWS_TO_CRAWL * 2]  # Get extra in case some fail
                        break
                
                if not review_elements:
                    print(f"⚠️ No review elements found with any selector")
                
                collected = 0
                for idx, review_elem in enumerate(review_elements):
                    if collected >= REVIEWS_TO_CRAWL:
                        break
                    
                    try:
                        # Get reviewer name - try multiple approaches
                        reviewer_name = 'Anonymous'
                        name_selectors = [
                            'button[aria-label]',
                            'div.d4r55',
                            'div[class*="name"]',
                            'a[href*="/contrib/"]'
                        ]
                        for sel in name_selectors:
                            name_elem = review_elem.locator(sel).first
                            if name_elem.count() > 0:
                                try:
                                    reviewer_name = name_elem.inner_text() or name_elem.get_attribute('aria-label')
                                    if reviewer_name:
                                        break
                                except:
                                    pass
                        
                        # Get review text - try multiple selectors
                        review_text = ''
                        text_selectors = [
                            'span.wiI7pd',
                            'div.MyEned',
                            'span[class*="review"]',
                            'div[class*="review"] span'
                        ]
                        for sel in text_selectors:
                            text_elem = review_elem.locator(sel).first
                            if text_elem.count() > 0:
                                try:
                                    review_text = text_elem.inner_text()
                                    if review_text:
                                        break
                                except:
                                    pass
                        
                        # Get rating
                        review_rating = 0
                        star_elem = review_elem.locator('[role="img"][aria-label*="star"]').first
                        if star_elem.count() > 0:
                            try:
                                aria = star_elem.get_attribute('aria-label')
                                rating_match = re.search(r'(\d+)', aria)
                                if rating_match:
                                    review_rating = int(rating_match.group(1))
                            except:
                                pass
                        
                        # Only save if we have meaningful content
                        if review_text.strip() and len(review_text) > 10:
                            reviews.append({
                                'reviewer': reviewer_name[:100],
                                'rating': review_rating,
                                'text': review_text[:500]
                            })
                            collected += 1
                            print(f"   ✅ Review {collected}: {reviewer_name[:30]} ({review_rating}⭐) - {review_text[:40]}...")
                    except Exception as e:
                        pass
                
                if len(reviews) > 0:
                    print(f"✅ Collected {len(reviews)} reviews")
                else:
                    print(f"⚠️ No reviews collected")
                    
            except Exception as e:
                result['errors'].append(f"Reviews: {str(e)}")
                print(f"⚠️ Reviews error: {str(e)[:80]}")
            
            # Go back to main view
            try:
                page.keyboard.press('Escape')
                time.sleep(1)
            except:
                pass
            
            # ============ PHOTOS ============
            print(f"\n📸 Downloading photos...")
            photos = []
            
            # Create place-specific folder
            place_slug = slugify(data.get('name', name_hint))
            place_photo_dir = os.path.join(photos_dir, place_slug)
            os.makedirs(place_photo_dir, exist_ok=True)
            
            try:
                # Find Photos button - try multiple selectors
                photos_button = None
                photo_selectors = [
                    'button:has-text("Photos")',
                    'button:has-text("Photo")',
                    'button[aria-label*="Photo"]',
                    'button[jsaction*="photo"]'
                ]
                
                for selector in photo_selectors:
                    elem = page.locator(selector).first
                    if elem.count() > 0:
                        photos_button = elem
                        break
                
                if photos_button:
                    photos_button.click()
                    time.sleep(3)  # Wait for gallery to load
                    
                    # Collection strategy: use the main gallery container
                    downloaded = 0
                    seen_urls = set()
                    scroll_attempts = 0
                    max_scrolls = 10
                    
                    while downloaded < PHOTOS_PER_PLACE and scroll_attempts < max_scrolls:
                        # Get all image elements
                        img_elements = page.locator('img[src*="googleusercontent"]').all()
                        
                        # Process images
                        for img_elem in img_elements:
                            if downloaded >= PHOTOS_PER_PLACE:
                                break
                            
                            try:
                                src = img_elem.get_attribute('src')
                                if not src or 'googleusercontent' not in src:
                                    continue
                                
                                # Skip if we've seen this URL
                                if src in seen_urls:
                                    continue
                                
                                seen_urls.add(src)
                                
                                # Modify URL for higher quality
                                src = re.sub(r'=w\d+-h\d+', '=w1920-h1080', src)
                                src = re.sub(r'=s\d+', '=s1920', src)
                                
                                # Download
                                filename = f"image_{downloaded+1:03d}.jpg"
                                save_path = os.path.join(place_photo_dir, filename)
                                
                                if download_image(src, save_path):
                                    photos.append({
                                        'filename': filename,
                                        'path': save_path,
                                        'url': src
                                    })
                                    downloaded += 1
                                    
                                    if downloaded % 5 == 0:
                                        print(f"   📥 Downloaded {downloaded}/{PHOTOS_PER_PLACE}")
                            
                            except Exception as e:
                                pass
                        
                        # Scroll down in photo gallery to load more
                        if downloaded < PHOTOS_PER_PLACE:
                            try:
                                # Scroll using arrow keys
                                for _ in range(3):
                                    page.keyboard.press('ArrowRight')
                                    time.sleep(0.3)
                                
                                scroll_attempts += 1
                            except:
                                break
                    
                    print(f"✅ Downloaded {len(photos)} photos to: {place_photo_dir}/")
                    
                    # Close photos gallery
                    try:
                        page.keyboard.press('Escape')
                        time.sleep(1)
                    except:
                        pass
                else:
                    print(f"⚠️ Could not find Photos button")
                    
            except Exception as e:
                result['errors'].append(f"Photos: {str(e)}")
                print(f"⚠️ Photos error: {str(e)[:80]}")
            
            browser.close()
            
            # Store results
            result['data'] = data
            result['reviews'] = reviews
            result['photos'] = photos
            result['success'] = len(data) > 0
            
            # Summary
            print(f"\n{'='*80}")
            print(f"📊 SUMMARY:")
            print(f"   Data fields: {len(data)}")
            print(f"   Reviews: {len(reviews)}")
            print(f"   Photos: {len(photos)}")
            print(f"   Errors: {len(result['errors'])}")
            print('='*80)
            
    except Exception as e:
        result['errors'].append(f"Fatal: {str(e)}")
        print(f"❌ FAILED: {str(e)}")
    
    return result

def main():
    """Test enhanced crawler with sample URLs"""
    
    # Create directories
    os.makedirs(PHOTOS_BASE_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Test URLs
    test_urls = [
        ('La Maison 1888', 'https://maps.app.goo.gl/Ld7bX9nzGFbq3AmKA'),
        ('Roots Coffee', 'https://maps.app.goo.gl/jd76y9kdyHuQcRXx5'),
        ('InterContinental Danang', 'https://maps.google.com/?cid=6547822829102607629')
    ]
    
    print("="*80)
    print("🚀 ENHANCED GOOGLE MAPS CRAWLER")
    print(f"📸 Photos per place: {PHOTOS_PER_PLACE}")
    print(f"📝 Reviews per place: {REVIEWS_TO_CRAWL}")
    print("="*80)
    
    all_results = []
    
    for name, url in test_urls:
        result = crawl_google_maps_enhanced(url, name, PHOTOS_BASE_DIR)
        all_results.append(result)
        time.sleep(3)  # Rate limiting
    
    # Save results
    output_file = os.path.join(OUTPUT_DIR, 'enhanced_crawl_results.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        # Don't save full photo paths in JSON, just counts
        results_to_save = []
        for r in all_results:
            r_copy = r.copy()
            r_copy['photos_count'] = len(r['photos'])
            r_copy['photos'] = [{'filename': p['filename']} for p in r['photos'][:3]]  # Save only first 3 filenames
            results_to_save.append(r_copy)
        
        json.dump(results_to_save, f, indent=2, ensure_ascii=False)
    
    # Final summary
    print("\n" + "="*80)
    print("🎉 FINAL SUMMARY")
    print("="*80)
    
    total_photos = sum(len(r['photos']) for r in all_results)
    total_reviews = sum(len(r['reviews']) for r in all_results)
    
    for i, result in enumerate(all_results, 1):
        print(f"\n{i}. {result['name']}")
        print(f"   Status: {'✅ Success' if result['success'] else '❌ Failed'}")
        print(f"   Data fields: {len(result['data'])}")
        print(f"   Reviews: {len(result['reviews'])}")
        print(f"   Photos: {len(result['photos'])}")
        if result['errors']:
            print(f"   ⚠️ Errors: {len(result['errors'])}")
    
    print(f"\n{'='*80}")
    print(f"📊 TOTALS:")
    print(f"   Places crawled: {len(all_results)}")
    print(f"   Photos downloaded: {total_photos}")
    print(f"   Reviews collected: {total_reviews}")
    print(f"\n📁 Data saved to:")
    print(f"   JSON: {output_file}")
    print(f"   Photos: {PHOTOS_BASE_DIR}/")
    print("="*80)

if __name__ == '__main__':
    main()
