#!/usr/bin/env python3
"""
Production-grade Google Maps crawler with network interception
Handles lazy loading for 20 photos + 50 reviews per place
"""

from playwright.sync_api import sync_playwright, expect
import json
import time
import re
import os
import requests
from pathlib import Path
from collections import defaultdict

# Configuration
PHOTOS_PER_PLACE = 30  # Increased from 20
REVIEWS_TO_CRAWL = 20  # Reduced from 50 for reliability
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
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return True
    except:
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

def crawl_photos_with_network(page, place_name, photos_dir):
    """Crawl photos using network request interception"""
    print(f"\n📸 Crawling photos with network monitoring...")
    
    photos = []
    place_slug = slugify(place_name)
    place_photo_dir = os.path.join(photos_dir, place_slug)
    os.makedirs(place_photo_dir, exist_ok=True)
    
    # Track image URLs from network
    image_urls = set()
    
    def handle_response(response):
        """Intercept image responses"""
        url = response.url
        if 'googleusercontent.com' in url and response.status == 200:
            image_urls.add(url)
    
    page.on('response', handle_response)
    
    try:
        # Click main photo to open gallery
        main_photo = page.locator('button[aria-label*="Photo of"]').first
        if main_photo.count() == 0:
            main_photo = page.locator('button:has-text("See photos")').first
        
        if main_photo.count() > 0:
            print(f"   Opening photo gallery...")
            main_photo.click()
            time.sleep(3)
            
            # Strategy: Navigate through all photos to trigger loading
            print(f"   Navigating through photos...")
            navigated = 0
            max_navigations = PHOTOS_PER_PLACE + 10  # Extra buffer for 30 photos
            
            for i in range(max_navigations):
                # Wait for current image to load
                page.wait_for_load_state('networkidle', timeout=5000)
                time.sleep(0.5)
                
                # Try to navigate to next
                try:
                    # Method 1: Click next button
                    next_btn = page.locator('button[aria-label*="Next"]').first
                    if next_btn.count() > 0 and next_btn.is_visible():
                        next_btn.click()
                        navigated += 1
                    else:
                        # Method 2: Use keyboard
                        page.keyboard.press('ArrowRight')
                        navigated += 1
                    
                    time.sleep(0.8)
                    
                    if navigated % 5 == 0:
                        print(f"   Navigated {navigated} photos, collected {len(image_urls)} URLs")
                    
                except:
                    break
            
            print(f"   Collected {len(image_urls)} unique image URLs")
            
            # Download images
            downloaded = 0
            for url in list(image_urls)[:PHOTOS_PER_PLACE]:
                # Upgrade to high quality
                url_hq = re.sub(r'=w\d+-h\d+', '=w1920-h1080', url)
                url_hq = re.sub(r'=s\d+', '=s1920', url_hq)
                
                filename = f"photo_{downloaded+1:03d}.jpg"
                save_path = os.path.join(place_photo_dir, filename)
                
                if download_image(url_hq, save_path):
                    photos.append({
                        'filename': filename,
                        'path': save_path,
                        'url': url_hq
                    })
                    downloaded += 1
                    
                    if downloaded % 5 == 0:
                        print(f"   📥 Downloaded {downloaded}/{PHOTOS_PER_PLACE}")
            
            print(f"   ✅ Downloaded {len(photos)} photos")
            
            # Close gallery
            page.keyboard.press('Escape')
            time.sleep(1)
        else:
            print(f"   ⚠️ Could not find photo gallery button")
    
    except Exception as e:
        print(f"   ❌ Photo error: {str(e)[:100]}")
    
    finally:
        page.remove_listener('response', handle_response)
    
    return photos

def crawl_reviews_with_scroll(page):
    """Crawl reviews with smart scrolling"""
    print(f"\n📝 Crawling reviews with scrolling...")
    
    reviews = []
    
    try:
        # Find and click Reviews tab/section
        print(f"   Looking for reviews section...")
        
        # Strategy 1: Look for rating button with review count
        found = False
        buttons = page.locator('button').all()
        
        for btn in buttons[:100]:
            try:
                text = btn.inner_text()
                aria = btn.get_attribute('aria-label') or ''
                
                # Check if it's reviews section (has numbers and "review")
                if 'review' in text.lower() and any(c.isdigit() for c in text):
                    print(f"   Found reviews: {text[:50]}")
                    btn.scroll_into_view_if_needed()
                    time.sleep(0.5)
                    btn.click()
                    time.sleep(3)
                    found = True
                    break
            except:
                continue
        
        if not found:
            print(f"   ⚠️ Could not find reviews section")
            return reviews
        
        # Click "More" buttons to expand truncated reviews
        print(f"   Expanding reviews...")
        try:
            more_buttons = page.locator('button:has-text("More")').all()
            clicked = 0
            for btn in more_buttons[:20]:  # Click first 20 More buttons
                try:
                    if btn.is_visible():
                        btn.click()
                        clicked += 1
                        time.sleep(0.2)
                except:
                    pass
            if clicked > 0:
                print(f"   Clicked {clicked} 'More' buttons")
        except:
            pass
        
        # Now scroll to load all reviews
        print(f"   Scrolling to load reviews...")
        
        # Find scrollable container
        scrollable = page.locator('div[role="main"]').first
        if scrollable.count() == 0:
            scrollable = page.locator('.m6QErb.XiKgde').first
        
        # Scroll multiple times - MORE scrolling for MORE reviews
        prev_height = 0
        scroll_attempts = 0
        max_scrolls = 30  # Increased from 15
        
        for scroll_round in range(max_scrolls):
            try:
                if scrollable.count() > 0:
                    # Get current height
                    curr_height = scrollable.evaluate('el => el.scrollHeight')
                    
                    # Scroll to bottom
                    scrollable.evaluate('el => el.scrollTop = el.scrollHeight')
                    time.sleep(1.0)
                    
                    # Check if new content loaded
                    new_height = scrollable.evaluate('el => el.scrollHeight')
                    if new_height == curr_height:
                        scroll_attempts += 1
                        if scroll_attempts >= 3:  # Stop if no new content after 3 tries
                            print(f"   No more content to load after {scroll_round + 1} scrolls")
                            break
                    else:
                        scroll_attempts = 0  # Reset if content loaded
                        prev_height = new_height
                else:
                    page.mouse.wheel(0, 1500)
                    time.sleep(1.0)
                
                if (scroll_round + 1) % 5 == 0:
                    print(f"   Scrolled {scroll_round + 1} times...")
                    
            except:
                pass
        
        # Now extract reviews
        print(f"   Extracting review data...")
        
        # Try multiple selectors for review containers
        review_containers = []
        selectors = [
            'div.jftiEf',  # Standard
            'div.fontBodyMedium',
            'div[data-review-id]',
            'div[jslog*="review"]',
        ]
        
        for selector in selectors:
            containers = page.locator(selector).all()
            if len(containers) >= 5:  # Need at least 5
                review_containers = containers
                print(f"   Using selector: {selector} ({len(containers)} elements)")
                break
        
        if not review_containers:
            print(f"   ⚠️ No review containers found")
            return reviews
        
        # Extract review data
        collected = 0
        for container in review_containers[:REVIEWS_TO_CRAWL * 2]:  # Try extra in case some fail
            if collected >= REVIEWS_TO_CRAWL:
                break
            
            try:
                full_text = container.inner_text()
                
                # Skip if too short
                if len(full_text) < 20:
                    continue
                
                # Extract reviewer name
                reviewer = 'Anonymous'
                name_elems = container.locator('button, a[href*="/contrib/"], div.d4r55').all()
                for elem in name_elems[:3]:
                    try:
                        name = elem.inner_text()
                        if name and len(name) < 100 and len(name) > 2:
                            reviewer = name.strip()
                            break
                    except:
                        pass
                
                # Extract rating
                rating = 0
                star_elem = container.locator('[role="img"][aria-label*="star"]').first
                if star_elem.count() > 0:
                    aria = star_elem.get_attribute('aria-label')
                    match = re.search(r'(\d+)\s*star', aria)
                    if match:
                        rating = int(match.group(1))
                
                # Extract review text
                review_text = ''
                text_selectors = ['span.wiI7pd', 'div.MyEned', 'span.rsqaWe']
                for sel in text_selectors:
                    elem = container.locator(sel).first
                    if elem.count() > 0:
                        try:
                            text = elem.inner_text()
                            if text and len(text) > 20:
                                review_text = text
                                break
                        except:
                            pass
                
                # If no structured text, use full text
                if not review_text and len(full_text) > 20:
                    # Try to extract meaningful part
                    lines = full_text.split('\n')
                    for line in lines:
                        if len(line) > 20 and not line.startswith('More'):
                            review_text = line
                            break
                
                # Save if we have content
                if review_text and len(review_text) > 15:
                    reviews.append({
                        'reviewer': reviewer[:100],
                        'rating': rating,
                        'text': review_text[:800]
                    })
                    collected += 1
                    
                    if collected % 10 == 0:
                        print(f"   ✅ Collected {collected}/{REVIEWS_TO_CRAWL}")
                
            except Exception as e:
                continue
        
        print(f"   ✅ Total reviews: {len(reviews)}")
        
        # Go back
        page.keyboard.press('Escape')
        time.sleep(1)
    
    except Exception as e:
        print(f"   ❌ Reviews error: {str(e)[:100]}")
    
    return reviews

def crawl_place_advanced(url, name_hint, photos_dir):
    """Advanced crawler with network monitoring"""
    print(f"\n{'='*80}")
    print(f"🎯 CRAWLING: {name_hint}")
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
            browser = p.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled']
            )
            page = browser.new_page(viewport={'width': 1920, 'height': 1080})
            
            # Set user agent
            page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            print("⏳ Loading page...")
            page.goto(url, wait_until='networkidle', timeout=30000)
            time.sleep(3)
            
            data = {}
            
            # ===== BASIC INFO =====
            print("\n📋 Extracting basic info...")
            
            # Name
            try:
                data['name'] = page.locator('h1').first.inner_text()
                print(f"✅ Name: {data['name']}")
            except:
                pass
            
            # Rating
            try:
                rating_elem = page.locator('[role="img"][aria-label*="star"]').first
                aria_label = rating_elem.get_attribute('aria-label')
                match = re.search(r'(\d+\.?\d*)\s*star', aria_label)
                if match:
                    data['rating'] = float(match.group(1))
                    print(f"✅ Rating: {data['rating']} ⭐")
            except:
                pass
            
            # Address
            try:
                data['address'] = page.locator('button[data-item-id^="address"]').first.inner_text().strip()
                print(f"✅ Address: {data['address'][:60]}...")
            except:
                pass
            
            # Coordinates
            lat, lng = extract_coordinates_from_url(page.url)
            if lat and lng:
                data['coordinates'] = {'lat': lat, 'lng': lng}
                print(f"✅ Coordinates: {lat}, {lng}")
            

            # Category
            try:
                data['category'] = page.locator('button[jsaction*="category"]').first.inner_text()
                print(f"✅ Category: {data['category']}")
            except:
                pass
            
            # Phone
            try:
                data['phone'] = page.locator('button[data-item-id^="phone"]').first.inner_text().strip()
                print(f"✅ Phone: {data['phone']}")
            except:
                pass
            
            # Website
            try:
                data['website'] = page.locator('a[data-item-id^="authority"]').first.get_attribute('href')
                print(f"✅ Website: {data['website'][:50]}...")
            except:
                pass
            
            # ===== PHOTOS =====
            photos = crawl_photos_with_network(page, data.get('name', name_hint), photos_dir)
            
            # ===== REVIEWS =====
            reviews = crawl_reviews_with_scroll(page)
            
            browser.close()
            
            result['data'] = data
            result['photos'] = photos
            result['reviews'] = reviews
            result['success'] = len(data) > 0
            
            print(f"\n{'='*80}")
            print(f"📊 FINAL SUMMARY:")
            print(f"   ✅ Data fields: {len(data)}")
            print(f"   📸 Photos: {len(photos)}/{PHOTOS_PER_PLACE}")
            print(f"   📝 Reviews: {len(reviews)}/{REVIEWS_TO_CRAWL}")
            print('='*80)
            
    except Exception as e:
        result['errors'].append(str(e))
        print(f"❌ FATAL ERROR: {str(e)}")
    
    return result

def main():
    os.makedirs(PHOTOS_BASE_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Test URLs
    test_urls = [
        ('Roots Coffee', 'https://maps.app.goo.gl/jd76y9kdyHuQcRXx5'),
    ]
    
    print("="*80)
    print("🚀 ADVANCED GOOGLE MAPS CRAWLER")
    print("📸 Target: 20 photos per place")
    print("📝 Target: 50 reviews per place")
    print("="*80)
    
    all_results = []
    
    for name, url in test_urls:
        result = crawl_place_advanced(url, name, PHOTOS_BASE_DIR)
        all_results.append(result)
        time.sleep(3)
    
    # Save results
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
    
    print("\n" + "="*80)
    print("🎉 CRAWLING COMPLETE")
    print("="*80)
    print(f"\n📁 Results: {output_file}")
    print(f"📁 Photos: {PHOTOS_BASE_DIR}/")
    print("="*80)

if __name__ == '__main__':
    main()
