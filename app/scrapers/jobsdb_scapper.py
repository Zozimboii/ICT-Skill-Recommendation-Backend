# app/scrapers/jobsdb_scapper.py
from playwright.sync_api import sync_playwright

def fetch_jobsdb(max_pages: int = 30, max_jobs: int = 1500):
    base_url = "https://th.jobsdb.com/th/jobs"
    jobs = {}  # key=link กันซ้ำ
    page_no = 1

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(locale="th-TH")
        page = context.new_page()

        while page_no <= max_pages and len(jobs) < max_jobs:
            url = f"{base_url}?page={page_no}"
            print(f"🔍 Visiting page {page_no}")

            page.goto(url, wait_until="domcontentloaded", timeout=60000)

            # ✅ TODO: เปลี่ยน selector ให้ตรงโปรเจคคุณ
            cards = page.locator("article")  # ตัวอย่าง
            count = cards.count()

            if count == 0:
                print("❌ No jobs found -> stop")
                break

            new_count = 0
            for i in range(count):
                card = cards.nth(i)

                # ✅ TODO: เปลี่ยน selector ให้ตรงโปรเจคคุณ
                title = card.locator("h1, h2, h3").first.inner_text().strip() if card.locator("h1, h2, h3").count() else ""
                link = card.locator("a").first.get_attribute("href") if card.locator("a").count() else None

                if not link:
                    continue

                if link not in jobs:
                    jobs[link] = {"title": title, "link": link}
                    new_count += 1

                if len(jobs) >= max_jobs:
                    break

            print(f"Found {count} jobs | New: {new_count}")

            # ✅ ถ้าหน้านี้ไม่มีงานใหม่แล้ว ให้หยุด (กันวนยาว)
            if new_count == 0:
                print("❌ No new jobs -> stop")
                break

            page_no += 1

        browser.close()

    return list(jobs.values())
