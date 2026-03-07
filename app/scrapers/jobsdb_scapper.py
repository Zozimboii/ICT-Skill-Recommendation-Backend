# scrapers/jobsdb_scrapper.py
import re
from playwright.sync_api import sync_playwright
import time



def extract_job_id(url: str):
    match = re.search(r"/job/(\d+)", url)
    return int(match.group(1)) if match else None

def fetch_job_description(detail_page, url: str) -> str:
    """
    เข้าไปหน้า Job Detail แล้วดึง Job Description
    """
    try:
        detail_page.goto(url, wait_until="networkidle", timeout=60000)

        desc_el = detail_page.locator("[data-automation='jobAdDetails']")

        if desc_el.count():
            return desc_el.inner_text().strip()

        return ""

    except Exception:
        return ""


def fetch_jobsdb(max_pages: int = 1, max_jobs: int = 200):
    """
    Scrape JobsDB:
    - title
    - link
    - posted date text
    - description
    """

    base_url = "https://th.jobsdb.com/th/jobs"
    jobs = {}
    page_no = 1

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )

        page = context.new_page()

        while page_no <= max_pages and len(jobs) < max_jobs:
            url = f"{base_url}?page={page_no}"
            print(f"\n🔍 Visiting page {page_no} | Collected: {len(jobs)}")

            try:
                page.goto(url, wait_until="networkidle", timeout=60000)
                page.wait_for_selector("article", timeout=15000)

            except Exception:
                print(f"⚠️ Page {page_no} timeout. Skipping...")
                page_no += 1
                continue

            cards = page.locator("article")
            count = cards.count()

            if count == 0:
                print("❌ No job cards found. Stop scraping.")
                break

            for i in range(count):
                if len(jobs) >= max_jobs:
                    break

                card = cards.nth(i)

                try:
                    # ----------------------------
                    # 1) Title
                    # ----------------------------
                    title_el = card.locator("h1, h2, h3").first
                    title = title_el.inner_text().strip() if title_el.count() else ""

                    company_el = card.locator("[data-automation='jobCompany']").first
                    company_name = company_el.inner_text().strip() if company_el.count() else "N/A"
                    # ----------------------------
                    # 2) Link
                    # ----------------------------
                    link_el = card.locator("a").first
                    link = link_el.get_attribute("href")

                    if not link:
                        continue

                    full_link = (
                        f"https://th.jobsdb.com{link}"
                        if link.startswith("/")
                        else link
                    )

                    if full_link in jobs:
                        continue

                    # ----------------------------
                    # 3) Posted Date
                    # ----------------------------
                    # 3) Posted Date Text (FIX STRICT MODE)
                    time_el = card.locator("[data-automation='jobListingDate']").first
                    posted_text = time_el.inner_text().strip() if time_el.count() else ""

                    
                    # ----------------------------
                    # 4) Description (Correct way)
                    # ----------------------------
                    print(f"   📌 Fetching detail: {title[:40]}...")

                    detail_page = context.new_page()
                    description = fetch_job_description(detail_page, full_link)
                    detail_page.close()

                    time.sleep(0.3)

                    # ----------------------------
                    # Save
                    # ----------------------------
                    job_id = extract_job_id(full_link)
                    jobs[full_link] = {
                        "job_id": job_id,
                        "title": title,
                        "link": full_link,
                        "posted_at_text": posted_text,
                        "description": description,
                        "company_name": company_name,
                    }

                except Exception as e:
                    print("⚠️ Error parsing card:", e)
                    continue

            page_no += 1

        browser.close()

    print(f"\n✅ Done. Total jobs scraped: {len(jobs)}")
    return list(jobs.values())
