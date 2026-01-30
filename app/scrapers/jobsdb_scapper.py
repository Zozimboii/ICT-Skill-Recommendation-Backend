from playwright.sync_api import sync_playwright


def fetch_jobsdb(max_pages: int = 100, max_jobs: int = 5000):
    base_url = "https://th.jobsdb.com/th/jobs"
    jobs = {}
    page_no = 1

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # ปรับ User Agent เพื่อให้เหมือนคนใช้งานจริงมากขึ้น
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"  # noqa: E501
        )
        page = context.new_page()

        while page_no <= max_pages and len(jobs) < max_jobs:
            url = f"{base_url}?page={page_no}"
            print(f"🔍 Visiting page {page_no} | Collected: {len(jobs)}")

            try:
                # รอโหลดจนกว่า article จะปรากฏ
                page.goto(url, wait_until="networkidle", timeout=60000)
                page.wait_for_selector("article", timeout=10000)
            except:  # noqa: E722
                print(f"⚠️ Page {page_no} timeout or no articles. Moving on...")
                page_no += 1
                continue

            cards = page.locator("article")
            count = cards.count()
            if count == 0:
                break

            for i in range(count):
                card = cards.nth(i)
                try:
                    # ดึง Title และ Link
                    title_el = card.locator("h1, h2, h3").first
                    title = title_el.inner_text().strip() if title_el.count() else ""

                    link_el = card.locator("a").first
                    link = link_el.get_attribute("href") if link_el.count() else None

                    if not link:
                        continue
                    full_link = (
                        f"https://th.jobsdb.com{link}" if link.startswith("/") else link
                    )

                    # ✅ จุดสำคัญ: ดึงวันที่ประกาศงาน (Posted time)
                    # Selector นี้อิงตามโครงสร้าง JobsDB ปัจจุบัน
                    time_el = card.locator("[data-automation='jobListingDate']")
                    posted_text = (
                        time_el.inner_text().strip() if time_el.count() else ""
                    )

                    if full_link not in jobs:
                        jobs[full_link] = {
                            "title": title,
                            "link": full_link,
                            "posted_at_text": posted_text,  # ต้องส่งชื่อนี้ไปให้ update.py
                        }
                except Exception as e:  # noqa: F841
                    continue

            page_no += 1
        browser.close()
    return list(jobs.values())
