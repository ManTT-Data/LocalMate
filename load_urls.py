#!/usr/bin/env python3
"""
Load all URLs from Excel files and prepare for full crawl
"""

import pandas as pd
import json
import os

def load_all_urls_from_excel(sheet_dir):
    """Load all Google Maps URLs from Excel files"""
    
    excel_files = [
        '[5] Finding accommodation.xlsx',
        '[8] Food & Dining options.xlsx',
        '[9]Coffee shop in Danang.xlsx',
        '[12] Health & Fitness.xlsx',
        '[13]. Nightlife & Entertainment.xlsx'
    ]
    
    all_urls = []
    
    for filename in excel_files:
        filepath = os.path.join(sheet_dir, filename)
        if not os.path.exists(filepath):
            print(f"⚠️ File not found: {filename}")
            continue
        
        print(f"\n📖 Reading {filename}...")
        
        # Get all sheet names
        xl_file = pd.ExcelFile(filepath)
        print(f"   Found {len(xl_file.sheet_names)} sheets: {xl_file.sheet_names[:5]}...")
        
        file_count = 0
        
        # Read ALL sheets
        for sheet_name in xl_file.sheet_names:
            try:
                # Skip first row (title), use second row as header
                df = pd.read_excel(filepath, sheet_name=sheet_name, header=1)
                
                # Find name column
                name_column = None
                for col in df.columns:
                    col_lower = str(col).lower()
                    if 'place' in col_lower or 'name' in col_lower:
                        name_column = col
                        break
                
                # Find URL column  
                url_column = None
                for col in df.columns:
                    col_lower = str(col).lower()
                    if 'google' in col_lower or 'map' in col_lower or 'url' in col_lower:
                        url_column = col
                        break
                
                if not name_column or not url_column:
                    continue
                
                # Extract name and URL
                sheet_count = 0
                for _, row in df.iterrows():
                    name = row.get(name_column, 'Unknown')
                    url = row.get(url_column, '')
                    
                    # Skip if invalid
                    if pd.isna(name) or pd.isna(url):
                        continue
                    if not url or not isinstance(url, str) or 'maps' not in url.lower():
                        continue
                    
                    all_urls.append({
                        'name': str(name),
                        'url': str(url),
                        'source': filename,
                        'sheet': sheet_name
                    })
                    sheet_count += 1
                    file_count += 1
            
            except Exception as e:
                print(f"      ⚠️ Error reading {sheet_name}: {str(e)[:50]}")
                continue
        
        print(f"   ✅ Loaded {len([u for u in all_urls if u['source'] == filename])} URLs")
    
    return all_urls

def main():
    print("="*80)
    print("📊 LOADING ALL URLS FROM EXCEL")
    print("="*80)
    
    urls = load_all_urls_from_excel('sheet')
    
    print(f"\n{'='*80}")
    print(f"✅ TOTAL: {len(urls)} places")
    print("="*80)
    
    # Group by source
    by_source = {}
    for u in urls:
        source = u['source']
        by_source[source] = by_source.get(source, 0) + 1
    
    print("\nBreakdown by source:")
    for source, count in sorted(by_source.items()):
        print(f"  {source}: {count} places")
    
    # Save to JSON
    output_file = 'all_urls.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(urls, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Saved to: {output_file}")
    
    # Create Python list format for crawler
    print(f"\n📝 Creating crawler-ready format...")
    
    crawler_urls = []
    for u in urls:
        crawler_urls.append(f"    ('{u['name']}', '{u['url']}'),")
    
    with open('crawler_urls.txt', 'w', encoding='utf-8') as f:
        f.write("test_urls = [\n")
        f.write('\n'.join(crawler_urls))
        f.write("\n]\n")
    
    print(f"✅ Saved to: crawler_urls.txt")
    print(f"\n💡 Copy content from crawler_urls.txt to crawl_gmaps_production.py")

if __name__ == '__main__':
    main()
