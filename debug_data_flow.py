#!/usr/bin/env python3
# DEBUG SCRIPT
"""Debug script to check scraper and data flow"""

import re
from datetime import datetime, timedelta
from app.scrapers.jobsdb_scapper import fetch_jobsdb
from app.utils.category_mapping import map_category

def parse_posted_date(text):
    """Parse posted date from text like 'Listed more than sixteen days ago'"""
    today = datetime.now().date()
    if not text:
        return today, "No text"

    text_lower = text.lower()
    match = re.search(r"\d+", text_lower)
    if not match:
        return today, f"No number found in: {text}"
    
    value = int(match.group())

    if "day" in text_lower:
        return today - timedelta(days=value), f"Parsed {value} days ago"
    if "month" in text_lower:
        return today - timedelta(days=value * 30), f"Parsed {value} months ago"
    
    return today, f"No day/month keyword in: {text}"


def main():
    print("🔍 Step 1: Fetching jobs...")
    print("=" * 100)
    
    jobs = fetch_jobsdb(max_pages=2, max_jobs=100)
    print(f"\n✅ Got {len(jobs)} jobs from scraper\n")
    
    if not jobs:
        print("❌ No jobs fetched! Check scraper.")
        return
    
    # Check first 3 jobs
    print("=" * 100)
    print("🔍 Step 2: Inspecting first 5 jobs IN DETAIL...")
    print("=" * 100)
    
    for i, job in enumerate(jobs[:5], 1):
        print(f"\n{'='*100}")
        print(f"📌 JOB #{i}")
        print(f"{'='*100}")
        print(f"📝 Title: {job.get('title', 'N/A')}")
        print(f"📅 Posted: {job.get('posted_at_text', 'N/A')}")
        print(f"🔗 Link: {job.get('link', 'N/A')}")
        
        # Parse date
        parsed_date, note = parse_posted_date(job.get('posted_at_text', ''))
        print(f"📊 Parsed Date: {parsed_date} | ({note})")
        
        # Try to categorize
        title = job.get('title', '')
        cat = map_category(title)
        if cat:
            print(f"\n✅ CATEGORY FOUND:")
            print(f"   Main: {cat.get('main_category_name', 'N/A')}")
            print(f"   Sub: {cat.get('sub_category_name', 'N/A')}")
            print(f"   ID: {cat.get('sub_category_id', 'N/A')}")
            print(f"   Skills: {cat.get('skills', [])}")
        else:
            print(f"\n❌ NO CATEGORY MATCHED for: '{title}'")
    
    # Summary statistics
    print("\n" + "=" * 100)
    print("📊 Step 3: STATISTICS AND BREAKDOWN")
    print("=" * 100)
    
    categorized = 0
    uncategorized = 0
    category_breakdown = {}
    
    for job in jobs:
        cat = map_category(job.get('title', ''))
        if cat:
            categorized += 1
            cat_name = f"{cat['main_category_name']} > {cat['sub_category_name']}"
            category_breakdown[cat_name] = category_breakdown.get(cat_name, 0) + 1
        else:
            uncategorized += 1
    
    print(f"\n📈 Total jobs collected: {len(jobs)}")
    print(f"✅ Successfully categorized: {categorized} ({(categorized/len(jobs)*100):.1f}%)")
    print(f"❌ Failed to categorize: {uncategorized} ({(uncategorized/len(jobs)*100):.1f}%)")
    
    print(f"\n🏷️ CATEGORY BREAKDOWN:")
    for cat_name in sorted(category_breakdown, key=lambda x: category_breakdown[x], reverse=True):
        count = category_breakdown[cat_name]
        pct = (count / categorized) * 100 if categorized > 0 else 0
        print(f"   • {cat_name}: {count} jobs ({pct:.1f}%)")
    
    if uncategorized > 0:
        print(f"\n❓ UNCATEGORIZED JOB TITLES (showing first 10):")
        count = 0
        for job in jobs:
            if not map_category(job.get('title', '')):
                print(f"   {count+1}. {job.get('title', 'N/A')}")
                count += 1
                if count >= 10:
                    break

if __name__ == "__main__":
    main()
