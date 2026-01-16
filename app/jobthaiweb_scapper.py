# from playwright.sync_api import sync_playwright
# import time

# def fetch_jobthaiweb():
#     keywords = [
#         "software engineer",
#         "developer",
#         "programmer",
#         "web developer",
#         "system administrator",
#     ]

#     all_jobs = []

#     with sync_playwright() as p:
#         browser = p.chromium.launch(
#             headless=False,   # 🔴 สำคัญมาก
#             slow_mo=50
#         )

#         context = browser.new_context(
#             user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
#             viewport={"width": 1280, "height": 800},
#         )

#         page = context.new_page()

#         for keyword in keywords:
#             url = f"https://www.jobthaiweb.com/search?keyword={keyword.replace(' ', '+')}"
#             print(f"🔍 Visiting JobThaiWeb: {url}")

#             try:
#                 page.goto(url, timeout=60000)
#                 time.sleep(5)  # 🔴 รอ JS เต็มที่

#                 # 🔴 scroll เพื่อ trigger lazy load
#                 page.mouse.wheel(0, 3000)
#                 time.sleep(3)

#                 # selector กว้างที่สุด
#                 job_cards = page.locator("a")

#                 count = job_cards.count()
#                 print(f"🧪 Total <a> tags found: {count}")

#                 for i in range(count):
#                     href = job_cards.nth(i).get_attribute("href")
#                     title = job_cards.nth(i).inner_text().strip()

#                     if href and ("jobdetail" in href or "position" in href):
#                         if 3 < len(title) < 200:
#                             all_jobs.append({
#                                 "title": title,
#                                 "source": "jobthaiweb",
#                             })

#                 time.sleep(2)

#             except Exception as e:
#                 print(f"⚠️ Failed to scrape JobThaiWeb {url}: {e}")

#         browser.close()

#     print(f"✅ JobThaiWeb Playwright scraped: {len(all_jobs)} jobs")
#     return all_jobs
