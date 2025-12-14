#!/usr/bin/env python3
"""
Analyze Google Maps page structure by dumping HTML and finding selectors
Works in headless mode
"""

from playwright.sync_api import sync_playwright
import time
import json
import re

def analyze_page_structure(url, name):
    """Analyze and dump page structure"""
    print(f"\n{'='*80}")
    print(f"🔍 ANALYZING: {name}")
    print(f"URL: {url}")
    print('='*80)
    
    analysis = {
        'name': name,
        'url': url,
        'main_page': {},
        'photos_page': {},
        'reviews_page': {}
    }
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        # ========== MAIN PAGE ==========
        print("\n📍 STEP 1: Analyzing MAIN PAGE...")
        page.goto(url, wait_until='networkidle', timeout=30000)
        time.sleep(3)
        
        # Save HTML
        html_content = page.content()
        with open(f'data/analysis_{name.replace(" ", "_")}_main.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"   ✅ Saved main page HTML")
        
        # Find all buttons
        buttons = page.locator('button').all()
        button_info = []
        for i, btn in enumerate(buttons[:100]):  # First 100
            try:
                text = btn.inner_text()[:50]
                aria = btn.get_attribute('aria-label') or ''
                aria = aria[:50]
                if text or aria:
                    button_info.append({
                        'index': i,
                        'text': text,
                        'aria_label': aria
                    })
            except:
                pass
        
        analysis['main_page']['buttons'] = button_info
        print(f"   Found {len(button_info)} buttons")
        
        # Look for Photos button
        photo_buttons = [b for b in button_info if 'photo' in b['text'].lower() or 'photo' in b['aria_label'].lower()]
        print(f"\n   📸 Photo-related buttons: {len(photo_buttons)}")
        for pb in photo_buttons:
            print(f"      [{pb['index']}] text='{pb['text']}' aria='{pb['aria_label']}'")
        
        # Look for Reviews button  
        review_buttons = [b for b in button_info if 'review' in b['text'].lower() or 'review' in b['aria_label'].lower()]
        print(f"\n   📝 Review-related buttons: {len(review_buttons)}")
        for rb in review_buttons:
            print(f"      [{rb['index']}] text='{rb['text']}' aria='{rb['aria_label']}'")
        
        # ========== PHOTOS PAGE ==========
        print("\n\n📸 STEP 2: Analyzing PHOTOS PAGE...")
        
        # Try to click Photos button
        photo_clicked = False
        for selector in ['button[aria-label*="Photo"]', 'button:has-text("Photo")']:
            elem = page.locator(selector).first
            if elem.count() > 0:
                try:
                    elem.click()
                    time.sleep(3)
                    photo_clicked = True
                    print(f"   ✅ Clicked Photos button with: {selector}")
                    break
                except:
                    pass
        
        if photo_clicked:
            # Save photos page HTML
            photos_html = page.content()
            with open(f'data/analysis_{name.replace(" ", "_")}_photos.html', 'w', encoding='utf-8') as f:
                f.write(photos_html)
            print(f"   ✅ Saved photos page HTML")
            
            # Analyze image structure
            all_imgs = page.locator('img').all()
            google_imgs = page.locator('img[src*="googleusercontent"]').all()
            
            print(f"\n   Total images: {len(all_imgs)}")
            print(f"   Google images: {len(google_imgs)}")
            
            # Get sample image URLs
            sample_urls = []
            for img in google_imgs[:10]:
                src = img.get_attribute('src')
                if src:
                    sample_urls.append(src)
            
            analysis['photos_page'] = {
                'total_images': len(all_imgs),
                'google_images': len(google_imgs),
                'sample_urls': sample_urls
            }
            
            print("\n   Sample image URLs:")
            for i, url in enumerate(sample_urls[:3]):
                print(f"      [{i}] {url[:80]}...")
            
            # Look for navigation
            nav_buttons = page.locator('button[aria-label*="Next"], button[aria-label*="Previous"]').all()
            print(f"\n   Navigation buttons: {len(nav_buttons)}")
            for nb in nav_buttons[:5]:
                label = nb.get_attribute('aria-label')
                print(f"      - {label}")
            
            # Check for lightbox/gallery container
            print("\n   Looking for gallery container...")
            container_selectors = [
                'div[role="dialog"]',
                'div[class*="gallery"]',
                'div[class*="lightbox"]',
                'div[class*="viewer"]'
            ]
            for sel in container_selectors:
                count = page.locator(sel).count()
                if count > 0:
                    print(f"      {sel}: {count} found")
            
            # Close photos
            page.keyboard.press('Escape')
            time.sleep(2)
        else:
            print("   ❌ Could not open Photos")
        
        # ========== REVIEWS PAGE ==========
        print("\n\n📝 STEP 3: Analyzing REVIEWS PAGE...")
        
        # Try to click Reviews
        review_clicked = False
        for selector in ['button[aria-label*="Review"]', 'button:has-text("Review")']:
            elem = page.locator(selector).first
            if elem.count() > 0:
                try:
                    elem.click()
                    time.sleep(3)
                    review_clicked = True
                    print(f"   ✅ Clicked Reviews with: {selector}")
                    break
                except:
                    pass
        
        if review_clicked:
            # Save reviews page HTML
            reviews_html = page.content()
            with open(f'data/analysis_{name.replace(" ", "_")}_reviews.html', 'w', encoding='utf-8') as f:
                f.write(reviews_html)
            print(f"   ✅ Saved reviews page HTML")
            
            # Try multiple review selectors
            print("\n   Testing review selectors:")
            review_selectors = [
                'div[data-review-id]',
                'div[jslog*="review"]',
                'div.jftiEf',
                'div[role="article"]',
                'div.fontBodyMedium',
                'div[class*="review"]',
            ]
            
            selector_counts = {}
            for sel in review_selectors:
                count = page.locator(sel).count()
                selector_counts[sel] = count
                print(f"      {sel}: {count} elements")
            
            # Use best selector
            best_selector = max(selector_counts.items(), key=lambda x: x[1])
            print(f"\n   Best selector: {best_selector[0]} ({best_selector[1]} elements)")
            
            if best_selector[1] > 0:
                # Analyze first review
                first_review = page.locator(best_selector[0]).first
                
                print("\n   First review structure:")
                try:
                    # Get full text
                    full_text = first_review.inner_text()
                    print(f"      Full text (first 150 chars):")
                    print(f"      {full_text[:150]}...")
                    
                    # Save HTML snippet
                    review_html = first_review.inner_html()
                    with open(f'data/analysis_{name.replace(" ", "_")}_first_review.html', 'w', encoding='utf-8') as f:
                        f.write(review_html)
                    print(f"      ✅ Saved first review HTML snippet")
                    
                    # Try to extract components
                    print("\n   Trying to extract review components:")
                    
                    # Name
                    for name_sel in ['button', 'a[href*="contrib"]', 'div.d4r55', 'span[class*="name"]']:
                        elem = first_review.locator(name_sel).first
                        if elem.count() > 0:
                            text = elem.inner_text()
                            if text and len(text) < 50:
                                print(f"      Name ({name_sel}): {text}")
                                break
                    
                    # Rating
                    star_elem = first_review.locator('[role="img"][aria-label*="star"]').first
                    if star_elem.count() > 0:
                        aria = star_elem.get_attribute('aria-label')
                        print(f"      Rating: {aria}")
                    
                    # Text
                    for text_sel in ['span.wiI7pd', 'div.MyEned', 'span[class*="review"]']:
                        elem = first_review.locator(text_sel).first
                        if elem.count() > 0:
                            text = elem.inner_text()
                            if text and len(text) > 10:
                                print(f"      Review text ({text_sel}): {text[:60]}...")
                                break
                    
                except Exception as e:
                    print(f"      ❌ Error analyzing review: {e}")
            
            analysis['reviews_page'] = {
                'selector_counts': selector_counts,
                'best_selector': best_selector[0]
            }
        else:
            print("   ❌ Could not open Reviews")
        
        browser.close()
    
    # Save analysis JSON
    with open(f'data/analysis_{name.replace(" ", "_")}.json', 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*80)
    print(f"✅ Analysis complete!")
    print(f"📁 Files saved:")
    print(f"   - data/analysis_{name.replace(' ', '_')}_main.html")
    print(f"   - data/analysis_{name.replace(' ', '_')}_photos.html")
    print(f"   - data/analysis_{name.replace(' ', '_')}_reviews.html")
    print(f"   - data/analysis_{name.replace(' ', '_')}_first_review.html")
    print(f"   - data/analysis_{name.replace(' ', '_')}.json")
    print("="*80)
    
    return analysis

def main():
    import os
    os.makedirs('data', exist_ok=True)
    
    # Test with Roots Coffee (has many reviews and photos)
    test_url = ('roots_coffee', 'https://maps.app.goo.gl/jd76y9kdyHuQcRXx5')
    
    print("="*80)
    print("🔍 GOOGLE MAPS STRUCTURE ANALYZER")
    print("="*80)
    print("\nThis will:")
    print("  1. Load the page")
    print("  2. Click Photos and analyze structure")
    print("  3. Click Reviews and analyze structure")
    print("  4. Save HTML dumps for manual inspection")
    print("\n")
    
    analysis = analyze_page_structure(test_url[1], test_url[0])
    
    print("\n📊 SUMMARY:")
    print(f"   Main page buttons: {len(analysis['main_page'].get('buttons', []))}")
    if 'total_images' in analysis.get('photos_page', {}):
        print(f"   Photos found: {analysis['photos_page']['google_images']}")
    if 'best_selector' in analysis.get('reviews_page', {}):
        print(f"   Reviews selector: {analysis['reviews_page']['best_selector']}")
    
    print("\n💡 Next: Open the saved HTML files to inspect structure manually")

if __name__ == '__main__':
    main()
