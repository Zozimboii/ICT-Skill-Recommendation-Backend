from playwright.sync_api import sync_playwright
from app.utils.category_mapping import map_category

def fetch_job_description(job_link: str) -> str:
    """ดึง detailed job description จากหน้างาน"""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            page.goto(job_link, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(1000)
            
            # ลองหา section ที่มี job description
            # โดยทั่วไป JobsDB จะมี section ที่ชื่อ "Job Description" หรือ "About the job"
            description_selectors = [
                "section",  # ดึงข้อความทั้งหมด
                "[data-automation*='description']",
                "div[class*='description']",
                "article"
            ]
            
            description = ""
            for selector in description_selectors:
                els = page.locator(selector)
                if els.count() > 0:
                    # ดึงข้อความจากหลาย elements
                    text_parts = []
                    for i in range(min(els.count(), 3)):  # เอาไม่เกิน 3 sections
                        text = els.nth(i).inner_text().strip()
                        if text and len(text) > 10:  # เอาเฉพาะที่มีข้อความสำคัญ
                            text_parts.append(text)
                    
                    if text_parts:
                        description = "\n\n".join(text_parts)[:1500]  # ตัดเป็น 1500 ตัวอักษร
                        break
            
            browser.close()
            return description
            
    except Exception as e:
        print(f"  ⚠️ Failed to fetch description for {job_link}: {e}")
        return ""


def fetch_jobsdb(max_pages: int = 100, max_jobs: int = 5000, fetch_details: bool = False):
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
                # ใช้ domcontentloaded แทน networkidle (รวดเร็วกว่า)
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(2000)  # รอให้ JS render เสร็จ
            except Exception as e:
                print(f"⚠️ Page {page_no} failed to load: {e}")
                page_no += 1
                continue

            cards = page.locator("article")
            count = cards.count()
            print(f"   📊 Found {count} articles")
            
            if count == 0:
                print(f"   ❌ No articles on page {page_no}, moving to next...")
                page_no += 1
                continue

            for i in range(count):
                card = cards.nth(i)
                try:
                    # ดึง link จาก data-automation="job-list-view-job-link"
                    link_el = card.locator("[data-automation='job-list-view-job-link']").first
                    if not link_el.count():
                        link_el = card.locator("a").first
                    
                    link = link_el.get_attribute("href") if link_el.count() else None
                    if not link:
                        continue
                    
                    full_link = (
                        f"https://th.jobsdb.com{link}" if link.startswith("/") else link
                    )

                    # ดึง title และ date จาก text content
                    # Format: "Listed X days ago\nJob Title\nCompany..."
                    all_text = card.inner_text().strip()
                    lines = all_text.split('\n')
                    
                    posted_text = lines[0] if lines else ""  # บรรทัดแรก: "Listed..."
                    title = lines[1].strip() if len(lines) > 1 else ""  # บรรทัดที่ 2: job title
                    
                    if not title:
                        continue

                    # ดึง description จากหน้า list (preview text)
                    # ลองหาข้อความส่วนที่นอก title, company, posted date
                    description = ""
                    try:
                        # description อาจอยู่ในบรรทัด 4 เป็นต้นไป (ข้ามบรรทัด date, title, company)
                        if len(lines) > 4:
                            # เชื่อมบรรทัด 5 ขึ้นไป เป็น description
                            desc_lines = [line.strip() for line in lines[4:] if line.strip()]
                            # ดึงเฉพาะบรรทัดแรก ๆ (ประมาณ 200 ตัวอักษร)
                            description = " ".join(desc_lines)[:300]
                    except:
                        pass

                    # กรองเฉพาะงาน Information & Technology
                    category = map_category(title)
                    if category and category.get("main_category_id") == 6281:  # ICT category
                        if full_link not in jobs:
                            jobs[full_link] = {
                                "title": title,
                                "link": full_link,
                                "posted_at_text": posted_text,
                                "description": description,
                                "category": category,  # เก็บข้อมูล category ด้วย
                            }
                except Exception as e:  # noqa: F841
                    continue

            page_no += 1
        browser.close()
    
    # ถ้า fetch_details=True ให้เข้าไปดึง detailed description
    if fetch_details and len(jobs) > 0:
        print(f"\n📄 Fetching detailed descriptions (this will take a while)...")
        for idx, job in enumerate(jobs):
            print(f"   [{idx+1}/{len(jobs)}] Fetching: {job['title'][:50]}...")
            detailed_desc = fetch_job_description(job['link'])
            if detailed_desc:
                job['description'] = detailed_desc
    
    return list(jobs.values())
