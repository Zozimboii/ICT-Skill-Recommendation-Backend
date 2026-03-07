import re
from playwright.sync_api import sync_playwright
import time

def extract_job_id(url: str):
    match = re.search(r"/job/(\d+)", url)
    return int(match.group(1)) if match else None

def fetch_job_description(detail_page, url: str) -> dict:
    try:
        detail_page.goto(url, wait_until="networkidle", timeout=60000)
        # ดึง Description
        desc_el = detail_page.locator("[data-automation='jobAdDetails']")
        description = desc_el.inner_text().strip() if desc_el.count() else ""
        
        # ดึงข้อมูลเพิ่มเติมจากหน้าใน (ถ้ามี) เช่น Category จริงๆ จาก breadcrumbs
        # แต่ในที่นี้จะใช้ AI หรือ Mapper ช่วยจัดการในขั้นตอนถัดไป
        return {"description": description}
    except Exception:
        return {"description": ""}

def fetch_jobsdb(max_pages: int = 5, max_jobs: int = 200):
    base_url = "https://th.jobsdb.com/th/jobs/"
    jobs = {}
    page_no = 1

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36..."
        )
        page = context.new_page()

        while page_no <= max_pages and len(jobs) < max_jobs:
            url = f"{base_url}?page={page_no}"
            print(f"\n🔍 Visiting page {page_no} | Collected: {len(jobs)}")

            try:
                page.goto(url, wait_until="networkidle", timeout=60000)
                page.wait_for_selector("article", timeout=15000)
            except Exception:
                page_no += 1
                continue

            cards = page.locator("article")
            for i in range(cards.count()):
                if len(jobs) >= max_jobs: break
                card = cards.nth(i)
                try:
                    title_el = card.locator("h1, h2, h3").first
                    title = title_el.inner_text().strip() if title_el.count() else ""
                    
                    link_el = card.locator("a").first
                    link = link_el.get_attribute("href")
                    if not link: continue
                    full_link = f"https://th.jobsdb.com{link}" if link.startswith("/") else link

                    if full_link in jobs: continue

                    time_el = card.locator("[data-automation='jobListingDate']").first
                    posted_text = time_el.inner_text().strip() if time_el.count() else ""

                    # ดึงข้อมูลบริษัท
                    company_el = card.locator("[data-automation='jobCardCompanyLink']").first
                    company = company_el.inner_text().strip() if company_el.count() else "Unknown Company"

                    print(f"   📌 Fetching detail: {title[:30]}...")
                    detail_page = context.new_page()
                    detail_data = fetch_job_description(detail_page, full_link)
                    detail_page.close()

                    job_id = extract_job_id(full_link)
                    jobs[full_link] = {
                        "job_id": job_id,
                        "title": title,
                        "company": company,
                        "link": full_link,
                        "posted_at_text": posted_text,
                        "description": detail_data["description"],
                    }
                    time.sleep(0.5)
                except Exception as e:
                    continue
            page_no += 1
        browser.close()
    return list(jobs.values())