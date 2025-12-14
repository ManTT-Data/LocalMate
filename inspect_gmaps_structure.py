#!/usr/bin/env python3
"""
Inspect Google Maps page structure to understand DOM and find correct selectors
Run in non-headless mode to see what's happening
"""

from playwright.sync_api import sync_playwright
import time

def inspect_google_maps(url, name):
    """Inspect page structure step by step"""
    print(f"\n{'='*80}")
    print(f"🔍 INSPECTING: {name}")
    print(f"URL: {url}")
    print('='*80)
    
    with sync_playwright() as p:
        # Launch in NON-HEADLESS mode to see what's happening
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        print("\n⏳ Step 1: Loading main page...")
        page.goto(url, wait_until='networkidle', timeout=30000)
        time.sleep(3)
        
        # Get page HTML structure
        print("\n📋 Step 2: Analyzing main page structure...")
        
        # Find all h1 elements (place name)
        h1_elements = page.locator('h1').all()
        print(f"   H1 elements found: {len(h1_elements)}")
        for i, elem in enumerate(h1_elements[:3]):
            print(f"      [{i}] {elem.inner_text()[:60]}")
        
        # Find rating elements
        rating_elements = page.locator('[role="img"][aria-label*="star"]').all()
        print(f"   Rating elements: {len(rating_elements)}")
        for i, elem in enumerate(rating_elements[:3]):
            print(f"      [{i}] {elem.get_attribute('aria-label')[:60]}")
        
        # Find all buttons
        all_buttons = page.locator('button').all()
        print(f"   Total buttons: {len(all_buttons)}")
        
        # Find Photos button
        print("\n📸 Step 3: Looking for Photos button...")
        photo_button_texts = []
        for button in all_buttons[:50]:  # Check first 50 buttons
            try:
                text = button.inner_text()
                aria_label = button.get_attribute('aria-label') or ''
                if 'photo' in text.lower() or 'photo' in aria_label.lower():
                    photo_button_texts.append((text, aria_label))
                    print(f"   Found: text='{text}', aria-label='{aria_label}'")
            except:
                pass
        
        # Find Reviews button
        print("\n📝 Step 4: Looking for Reviews button...")
        review_button_texts = []
        for button in all_buttons[:50]:
            try:
                text = button.inner_text()
                aria_label = button.get_attribute('aria-label') or ''
                if 'review' in text.lower() or 'review' in aria_label.lower():
                    review_button_texts.append((text, aria_label))
                    print(f"   Found: text='{text}', aria-label='{aria_label}'")
            except:
                pass
        
        # Click Photos button if found
        print("\n🖱️ Step 5: Attempting to open Photos gallery...")
        photos_opened = False
        
        # Try different selectors
        photo_selectors = [
            'button[aria-label*="hoto"]',
            'button[aria-label*="Photo"]',
            'button:has-text("Photos")',
            'button:has-text("Photo")',
        ]
        
        for selector in photo_selectors:
            button = page.locator(selector).first
            if button.count() > 0:
                try:
                    print(f"   Clicking: {selector}")
                    button.click()
                    time.sleep(3)
                    photos_opened = True
                    break
                except Exception as e:
                    print(f"   Failed: {str(e)[:50]}")
        
        if photos_opened:
            print("\n✅ Photos gallery opened!")
            print("   Analyzing photo gallery structure...")
            
            # Count images
            all_imgs = page.locator('img').all()
            print(f"   Total img elements: {len(all_imgs)}")
            
            googleusercontent_imgs = page.locator('img[src*="googleusercontent"]').all()
            print(f"   Images from googleusercontent: {len(googleusercontent_imgs)}")
            
            # Print first few image sources
            print("\n   First 5 image sources:")
            for i, img in enumerate(googleusercontent_imgs[:5]):
                src = img.get_attribute('src')
                print(f"      [{i}] {src[:100]}...")
            
            # Try to find navigation elements
            print("\n   Looking for navigation controls...")
            nav_buttons = page.locator('button[aria-label*="ext"], button[aria-label*="rev"]').all()
            print(f"   Navigation buttons: {len(nav_buttons)}")
            for btn in nav_buttons[:5]:
                label = btn.get_attribute('aria-label')
                print(f"      - {label}")
            
            # Check page structure
            print("\n   Checking current URL...")
            print(f"   {page.url}")
            
            input("\n⏸️  Press ENTER to continue to reviews test...")
            
            # Close photos
            page.keyboard.press('Escape')
            time.sleep(2)
        else:
            print("❌ Could not open Photos gallery")
            input("\n⏸️  Press ENTER to continue...")
        
        # Click Reviews button
        print("\n🖱️ Step 6: Attempting to open Reviews...")
        reviews_opened = False
        
        review_selectors = [
            'button[aria-label*="eview"]',
            'button[aria-label*="Review"]',
            'button:has-text("Reviews")',
            'button:has-text("Review")',
        ]
        
        for selector in review_selectors:
            button = page.locator(selector).first
            if button.count() > 0:
                try:
                    print(f"   Clicking: {selector}")
                    button.click()
                    time.sleep(3)
                    reviews_opened = True
                    break
                except Exception as e:
                    print(f"   Failed: {str(e)[:50]}")
        
        if reviews_opened:
            print("\n✅ Reviews section opened!")
            print("   Analyzing reviews structure...")
            
            # Try different review selectors
            review_container_selectors = [
                'div[data-review-id]',
                'div[jslog*="review"]',
                'div.jftiEf',
                'div[role="article"]',
                'div.fontBodyMedium',
            ]
            
            for selector in review_container_selectors:
                elements = page.locator(selector).all()
                print(f"   Selector '{selector}': {len(elements)} elements")
                
                if len(elements) > 0:
                    print(f"\n   Analyzing first review with '{selector}':")
                    first_review = elements[0]
                    
                    # Get all text content
                    try:
                        all_text = first_review.inner_text()
                        print(f"      Full text (first 200 chars):")
                        print(f"      {all_text[:200]}...")
                    except:
                        pass
                    
                    # Get HTML structure
                    try:
                        html = first_review.inner_html()
                        print(f"\n      HTML structure (first 300 chars):")
                        print(f"      {html[:300]}...")
                    except:
                        pass
                    
                    # Try to find reviewer name
                    name_selectors = ['button', 'a', 'div', 'span']
                    for sel in name_selectors:
                        names = first_review.locator(sel).all()
                        if len(names) > 0:
                            try:
                                text = names[0].inner_text()
                                if text and len(text) < 50:
                                    print(f"      Possible name ({sel}): {text}")
                            except:
                                pass
                    
                    break
            
            input("\n⏸️  Press ENTER to close browser...")
        else:
            print("❌ Could not open Reviews section")
            input("\n⏸️  Press ENTER to close browser...")
        
        browser.close()
        
        print("\n" + "="*80)
        print("✅ Inspection complete!")
        print("="*80)

def main():
    # Test URL
    test_url = ('Roots Coffee', 'https://maps.app.goo.gl/jd76y9kdyHuQcRXx5')
    
    print("="*80)
    print("🔍 GOOGLE MAPS STRUCTURE INSPECTOR")
    print("="*80)
    print("\n⚠️  This will open a visible browser window")
    print("   You can inspect the page manually while script runs")
    print("\nPress Ctrl+C to cancel, or ENTER to start...")
    input()
    
    inspect_google_maps(test_url[1], test_url[0])

if __name__ == '__main__':
    main()
