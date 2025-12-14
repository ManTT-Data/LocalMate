#!/usr/bin/env python3
"""
Accurate Google Maps crawler based on DOM analysis
Crawls 20 photos + 50 reviews per place
"""

from playwright.sync_api import sync_playwright
import json
import time
import re
import os
import requests
from pathlib import Path

# Configuration
PHOTOS_PER_PLACE = 20
REVIEWS_TO_CRAWL = 50
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
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return True
    except Exception as e:
        pass
    return False

def extract_coordinates_from_url(url):
    """Extract coordinates from Google Maps URL"""
    match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', url)
    if match:
        return float(match.group(1)), float(match.group(2))
    
    lat_match = re.search(r'!3d(-?\d+\.\d+)', url)
    lng_match = re.search(r'!4d(-?\d+\.\d+)', url)
    if lat_match and lng_match:
        return float(lat_match.group(1)), float(lng_match.group(1))
    
    return None, None

def crawl_photos_accurate(page, place_name, photos_dir):
    """Accurately crawl photos by navigating through gallery"""
    print(f"\n📸 Crawling photos...")
    
    photos = []
    place_slug = slugify(place_name)
    place_photo_dir = os.path.join(photos_dir, place_slug)
    os.makedirs(place_photo_dir, exist_ok=True)
    
    try:
        # Strategy 1: Click main photo to open gallery
        main_photo = page.locator('button[aria-label*="Photo of"]').first
        if main_photo.count() == 0:
            # Strategy 2: Click "See photos" button
            main_photo = page.locator('button:has-text("See photos")').first
        
        if main_photo.count() > 0:
            print(f"   Clicking photo gallery...")
            main_photo.click()
            time.sleep(3)
            
            downloaded = 0
            seen_urls = set()
            failed_navigations = 0
            max_failures = 5
            
            while downloaded < PHOTOS_PER_PLACE and failed_navigations < max_failures:
                # Get current image
                current_img = page.locator('img[src*="googleusercontent"]').first
                
                if current_img.count() > 0:
                    src = current_img.get_attribute('src')
                    
                    if src and src not in seen_urls and 'googleusercontent' in src:
                        seen_urls.add(src)
                        
                        # Upgrade to high quality
                        src_hq = re.sub(r'=w\d+-h\d+', '=w1920-h1080', src)
                        src_hq = re.sub(r'=s\d+', '=s1920', src_hq)
                        
                        # Download
                        filename = f"photo_{downloaded+1:03d}.jpg"
                        save_path = os.path.join(place_photo_dir, filename)
                        
                        if download_image(src_hq, save_path):
                            photos.append({
                                'filename': filename,
                                'path': save_path,
                                'url': src_hq
                            })
                            downloaded += 1
                            
                            if downloaded % 5 == 0:
                                print(f"   📥 {downloaded}/{PHOTOS_PER_PLACE} photos")
                            
                            failed_navigations = 0  # Reset on success
                
                # Navigate to next photo
                if downloaded < PHOTOS_PER_PLACE:
                    try:
                        # Click Next button or use arrow key
                        next_button = page.locator('button[aria-label*="Next"]').first
                        if next_button.count() > 0 and next_button.is_visible():
                            next_button.click()
                            time.sleep(0.5)
                        else:
                            page.keyboard.press('ArrowRight')
                            time.sleep(0.5)
                    except:
                        failed_navigations += 1
                        time.sleep(0.3)
            
            print(f"   ✅ Downloaded {len(photos)} photos")
            
            # Close gallery
            page.keyboard.press('Escape')
            time.sleep(1)
        else:
            print(f"   ⚠️ Could not find photo gallery button")
    
    except Exception as e:
        print(f"   ❌ Photo crawl error: {str(e)[:80]}")
    
    return photos

def crawl_reviews_accurate(page):
    """Accurately crawl reviews by scrolling through reviews section"""
    print(f"\n📝 Crawling reviews...")
    
    reviews = []
    
    try:
        # Find reviews section - look for rating/reviews count button
        reviews_section = None
        
        # Strategy 1: Find element with review count (e.g., "1.2K reviews")
        review_count_buttons = page.locator('button').all()
        for btn in review_count_buttons[:50]:
            try:
                text = btn.inner_text()
                if 'review' in text.lower() and any(char.isdigit() for char in text):
                    reviews_section = btn
                    break
            except:
                pass
        
        if reviews_section:
            print(f"   Clicking reviews section...")
            reviews_section.click()
            time.sleep(3)
            
            # Now we should be in reviews tab
            # Scroll to load more reviews
            scrollable_div = page.locator('div[role="main"]').first
            if scrollable_div.count() == 0:
                scrollable_div = page.locator('div.m6QErb').first  # Common scrollable container
            
            # Scroll multiple times to load reviews
            print(f"   Loading reviews...")
            for i in range(10):  # Scroll 10 times to load ~50 reviews
                try:
                    if scrollable_div.count() > 0:
                        scrollable_div.evaluate('el => el.scrollTop = el.scrollHeight')
                    else:
                        page.mouse.wheel(0, 1000)
                    time.sleep(0.8)
                except:
                    pass
            
            # Find review elements
            review_elements = []
            
            # Try different selectors based on analysis
            selectors_to_try = [
                'div.jftiEf',  # Standard review container
                'div.fontBodyMedium',  # From our analysis
                'div[data-review-id]',  # Review with ID
                'div[jslog*="review"]',  # Review jslog
            ]
            
            for selector in selectors_to_try:
                elements = page.locator(selector).all()
                if len(elements) >= 3:  # Need at least 3 to be valid
                    review_elements = elements
                    print(f"   Using selector: {selector} ({len(elements)} elements)")
                    break
            
            # Extract reviews
            collected = 0
            for elem in review_elements[:REVIEWS_TO_CRAWL * 2]:  # Try more in case some fail
                if collected >= REVIEWS_TO_CRAWL:
                    break
                
                try:
                    # Get reviewer name
                    reviewer_name = 'Anonymous'
                    name_selectors = [
                        'div.d4r55',  # Name class
                        'button.WEBjve',  # Name button
                        'a[href*="/contrib/"]',  # Contributor link
                    ]
                    
                    for sel in name_selectors:
                        name_elem = elem.locator(sel).first
                        if name_elem.count() > 0:
                            try:
                                name_text = name_elem.inner_text()
                                if name_text and len(name_text) < 100:
                                    reviewer_name = name_text.strip()
                                    break
                            except:
                                pass
                    
                    # Get rating
                    review_rating = 0
                    star_elem = elem.locator('[role="img"][aria-label*="star"]').first
                    if star_elem.count() > 0:
                        try:
                            aria = star_elem.get_attribute('aria-label')
                            rating_match = re.search(r'(\d+)\s*star', aria)
                            if rating_match:
                                review_rating = int(rating_match.group(1))
                        except:
                            pass
                    
                    # Get review text
                    review_text = ''
                    text_selectors = [
                        'span.wiI7pd',  # Review text span
                        'div.MyEned',  # Alternative text div
                        'span.rsqaWe',  # Another text class
                    ]
                    
                    for sel in text_selectors:
                        text_elem = elem.locator(sel).first
                        if text_elem.count() > 0:
                            try:
                                text = text_elem.inner_text()
                                if text and len(text) > 5:
                                    review_text = text
                                    break
                            except:
                                pass
                    
                    # Get review date
                    review_date = ''
                    date_elem = elem.locator('span.rsqaWe').first
                    if date_elem.count() > 0:
                        try:
                            review_date = date_elem.inner_text()
                        except:
                            pass
                    
                    # Only save if we have text content
                    if review_text and len(review_text) > 10:
                        reviews.append({
                            'reviewer': reviewer_name[:100],
                            'rating': review_rating,
                            'text': review_text[:800],  # Limit length
                            'date': review_date[:50]
                        })
                        collected += 1
                        
                        if collected % 10 == 0:
                            print(f"   ✅ {collected}/{REVIEWS_TO_CRAWL} reviews")
                
                except Exception as e:
                    pass
            
            print(f"   ✅ Collected {len(reviews)} reviews")
            
            # Go back
            page.keyboard.press('Escape')
            time.sleep(1)
        else:
            print(f"   ⚠️ Could not find reviews section")
    
    except Exception as e:
        print(f"   ❌ Reviews error: {str(e)[:80]}")
    
    return reviews

def crawl_google_maps_v2(url, name_hint, photos_dir):
    """Improved crawler with accurate photo and review extraction"""
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
            page = browser.new_page(viewport={'width': 1920, 'height': 1080})
            
            print("⏳ Loading page...")
            page.goto(url, wait_until='networkidle', timeout=30000)
            time.sleep(3)
            
            data = {}
            
            # ===== BASIC INFO =====
            
            # Name
            try:
                name_elem = page.locator('h1').first
                if name_elem.count() > 0:
                    data['name'] = name_elem.inner_text()
                    print(f"✅ Name: {data['name']}")
            except:
                pass
            
            # Rating & Reviews Count
            try:
                rating_elem = page.locator('[role="img"][aria-label*="star"]').first
                if rating_elem.count() > 0:
                    aria_label = rating_elem.get_attribute('aria-label')
                    rating_match = re.search(r'(\d+\.?\d*)\s*star', aria_label)
                    if rating_match:
                        data['rating'] = float(rating_match.group(1))
                        print(f"✅ Rating: {data['rating']} ⭐")
            except:
                pass
            
            # Address
            try:
                address_elem = page.locator('button[data-item-id^="address"]').first
                if address_elem.count() > 0:
                    data['address'] = address_elem.inner_text().strip()
                    print(f"✅ Address: {data['address'][:60]}...")
            except:
                pass
            
            # Coordinates
            current_url = page.url
            lat, lng = extract_coordinates_from_url(current_url)
            if lat and lng:
                data['coordinates'] = {'lat': lat, 'lng': lng}
                print(f"✅ Coordinates: {lat}, {lng}")
            
            # Category
            try:
                category_elem = page.locator('button[jsaction*="category"]').first
                if category_elem.count() > 0:
                    data['category'] = category_elem.inner_text()
                    print(f"✅ Category: {data['category']}")
            except:
                pass
            
            # Phone
            try:
                phone_elem = page.locator('button[data-item-id^="phone"]').first
                if phone_elem.count() > 0:
                    data['phone'] = phone_elem.inner_text().strip()
                    print(f"✅ Phone: {data['phone']}")
            except:
                pass
            
            # Website
            try:
                website_elem = page.locator('a[data-item-id^="authority"]').first
                if website_elem.count() > 0:
                    data['website'] = website_elem.get_attribute('href')
                    print(f"✅ Website: {data['website'][:50]}...")
            except:
                pass
            
            # ===== PHOTOS =====
            photos = crawl_photos_accurate(page, data.get('name', name_hint), photos_dir)
            
            # ===== REVIEWS =====
            reviews = crawl_reviews_accurate(page)
            
            browser.close()
            
            result['data'] = data
            result['photos'] = photos
            result['reviews'] = reviews
            result['success'] = len(data) > 0
            
            print(f"\n{'='*80}")
            print(f"📊 SUMMARY:")
            print(f"   Data fields: {len(data)}")
            print(f"   Reviews: {len(reviews)}")
            print(f"   Photos: {len(photos)}")
            print('='*80)
            
    except Exception as e:
        result['errors'].append(str(e))
        print(f"❌ FAILED: {str(e)}")
    
    return result

def main():
    os.makedirs(PHOTOS_BASE_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Test URLs
    test_urls = [
        ('Roots Coffee', 'https://maps.app.goo.gl/jd76y9kdyHuQcRXx5'),
        ('La Maison 1888', 'https://maps.app.goo.gl/Ld7bX9nzGFbq3AmKA'),
    ]
    
    print("="*80)
    print("🚀 ACCURATE GOOGLE MAPS CRAWLER V2")
    print(f"📸 Photos per place: {PHOTOS_PER_PLACE}")
    print(f"📝 Reviews per place: {REVIEWS_TO_CRAWL}")
    print("="*80)
    
    all_results = []
    
    for name, url in test_urls:
        result = crawl_google_maps_v2(url, name, PHOTOS_BASE_DIR)
        all_results.append(result)
        time.sleep(3)
    
    # Save results
    output_file = os.path.join(OUTPUT_DIR, 'crawl_results_v2.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        results_to_save = []
        for r in all_results:
            r_copy = r.copy()
            r_copy['photos_count'] = len(r['photos'])
            r_copy['reviews_count'] = len(r['reviews'])
            r_copy['photos_sample'] = [p['filename'] for p in r['photos'][:3]]
            r_copy['reviews_sample'] = r['reviews'][:2]
            del r_copy['photos']  # Don't save all photo paths
            results_to_save.append(r_copy)
        
        json.dump(results_to_save, f, indent=2, ensure_ascii=False)
    
    # Final summary
    print("\n" + "="*80)
    print("🎉 FINAL RESULTS")
    print("="*80)
    
    total_photos = sum(len(r['photos']) for r in all_results)
    total_reviews = sum(len(r['reviews']) for r in all_results)
    
    for i, result in enumerate(all_results, 1):
        print(f"\n{i}. {result['name']}")
        print(f"   Status: {'✅' if result['success'] else '❌'}")
        print(f"   Photos: {len(result['photos'])}/{PHOTOS_PER_PLACE}")
        print(f"   Reviews: {len(result['reviews'])}/{REVIEWS_TO_CRAWL}")
    
    print(f"\n{'='*80}")
    print(f"📊 TOTALS:")
    print(f"   Photos: {total_photos}/{len(all_results) * PHOTOS_PER_PLACE}")
    print(f"   Reviews: {total_reviews}/{len(all_results) * REVIEWS_TO_CRAWL}")
    print(f"\n📁 Saved to:")
    print(f"   JSON: {output_file}")
    print(f"   Photos: {PHOTOS_BASE_DIR}/")
    print("="*80)

if __name__ == '__main__':
    main()
