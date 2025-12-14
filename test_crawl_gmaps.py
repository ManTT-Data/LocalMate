#!/usr/bin/env python3
"""
Test script to crawl Google Maps URLs and extract needed information
"""

from playwright.sync_api import sync_playwright
import json
import time
import re

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

def crawl_google_maps(url, name):
    """Crawl a single Google Maps URL"""
    print(f"\n{'='*80}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    print('='*80)
    
    result = {
        'name': name,
        'url': url,
        'data': {},
        'success': False,
        'errors': []
    }
    
    try:
        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            print("⏳ Loading page...")
            page.goto(url, wait_until='networkidle', timeout=30000)
            time.sleep(3)  # Wait for dynamic content
            
            # Extract data
            data = {}
            
            # 1. Name
            try:
                name_elem = page.locator('h1').first
                if name_elem.count() > 0:
                    data['name'] = name_elem.inner_text()
                    print(f"✅ Name: {data['name']}")
            except Exception as e:
                result['errors'].append(f"Name error: {str(e)}")
            
            # 2. Rating
            try:
                rating_elem = page.locator('[role="img"][aria-label*="star"]').first
                if rating_elem.count() > 0:
                    aria_label = rating_elem.get_attribute('aria-label')
                    rating_match = re.search(r'(\d+\.?\d*)\s*star', aria_label)
                    if rating_match:
                        data['rating'] = float(rating_match.group(1))
                        print(f"✅ Rating: {data['rating']} ⭐")
            except Exception as e:
                result['errors'].append(f"Rating error: {str(e)}")
            
            # 3. Total Reviews
            try:
                reviews_elem = page.locator('button:has-text("reviews")').first
                if reviews_elem.count() > 0:
                    text = reviews_elem.inner_text()
                    reviews_match = re.search(r'([\d,]+)\s*review', text)
                    if reviews_match:
                        data['total_reviews'] = int(reviews_match.group(1).replace(',', ''))
                        print(f"✅ Reviews: {data['total_reviews']}")
            except Exception as e:
                result['errors'].append(f"Reviews error: {str(e)}")
            
            # 4. Address
            try:
                address_elem = page.locator('button[data-item-id^="address"]').first
                if address_elem.count() > 0:
                    data['address'] = address_elem.inner_text()
                    print(f"✅ Address: {data['address'][:50]}...")
            except Exception as e:
                result['errors'].append(f"Address error: {str(e)}")
            
            # 5. Coordinates (from URL)
            current_url = page.url
            lat, lng = extract_coordinates_from_url(current_url)
            if lat and lng:
                data['coordinates'] = {'lat': lat, 'lng': lng}
                print(f"✅ Coordinates: {lat}, {lng}")
            else:
                result['errors'].append("Could not extract coordinates")
            
            # 6. Opening Hours
            try:
                hours_button = page.locator('button:has-text("Hours")').first
                if hours_button.count() > 0:
                    hours_text = hours_button.inner_text()
                    data['opening_hours_text'] = hours_text
                    print(f"✅ Hours: {hours_text[:30]}...")
            except Exception as e:
                result['errors'].append(f"Hours error: {str(e)}")
            
            # 7. Category/Type
            try:
                category_elem = page.locator('button[jsaction*="category"]').first
                if category_elem.count() > 0:
                    data['category'] = category_elem.inner_text()
                    print(f"✅ Category: {data['category']}")
            except Exception as e:
                result['errors'].append(f"Category error: {str(e)}")
            
            # 8. Photos count
            try:
                photos_button = page.locator('button:has-text("Photos")').first
                if photos_button.count() > 0:
                    photos_text = photos_button.inner_text()
                    photos_match = re.search(r'([\d,]+)\s*photo', photos_text)
                    if photos_match:
                        data['photos_count'] = int(photos_match.group(1).replace(',', ''))
                        print(f"✅ Photos available: {data['photos_count']}")
            except Exception as e:
                result['errors'].append(f"Photos error: {str(e)}")
            
            # 9. Phone
            try:
                phone_elem = page.locator('button[data-item-id^="phone"]').first
                if phone_elem.count() > 0:
                    data['phone'] = phone_elem.inner_text()
                    print(f"✅ Phone: {data['phone']}")
            except Exception as e:
                pass  # Phone is optional
            
            # 10. Website
            try:
                website_elem = page.locator('a[data-item-id^="authority"]').first
                if website_elem.count() > 0:
                    data['website'] = website_elem.get_attribute('href')
                    print(f"✅ Website: {data['website'][:40]}...")
            except Exception as e:
                pass  # Website is optional
            
            browser.close()
            
            result['data'] = data
            result['success'] = len(data) > 0
            
            # Summary
            print(f"\n📊 Summary:")
            print(f"   Fields extracted: {len(data)}")
            print(f"   Errors: {len(result['errors'])}")
            
    except Exception as e:
        result['errors'].append(f"Browser error: {str(e)}")
        print(f"❌ Failed: {str(e)}")
    
    return result

def main():
    # Test URLs
    test_urls = [
        ('La Maison 1888', 'https://maps.app.goo.gl/Ld7bX9nzGFbq3AmKA'),
        ('Roots Coffee', 'https://maps.app.goo.gl/jd76y9kdyHuQcRXx5'),
        ('InterContinental Danang', 'https://maps.google.com/?cid=6547822829102607629')
    ]
    
    results = []
    
    for name, url in test_urls:
        result = crawl_google_maps(url, name)
        results.append(result)
        time.sleep(2)  # Be nice to Google
    
    # Final summary
    print("\n" + "="*80)
    print("FINAL SUMMARY - CRAWLING TEST RESULTS")
    print("="*80)
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['name']}")
        print(f"   Status: {'✅ Success' if result['success'] else '❌ Failed'}")
        print(f"   Data fields: {len(result['data'])}")
        
        # Check critical fields
        critical_fields = ['coordinates', 'rating', 'photos_count']
        missing = [f for f in critical_fields if f not in result['data']]
        if missing:
            print(f"   ⚠️ Missing critical: {', '.join(missing)}")
    
    # Save results
    output_file = '/media/thuongnv/New Volume/Code/thuongnvv/GrabTheBeyound2/crawl_test_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Full results saved to: {output_file}")
    print("="*80)

if __name__ == '__main__':
    main()
