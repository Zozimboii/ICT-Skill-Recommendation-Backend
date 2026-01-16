# from playwright.sync_api import sync_playwright
# import time

# def fetch_jobthai():
#     url = "https://www.jobthai.com/th/job_search.php?keyword=software+engineer"
#     jobs = []

#     with sync_playwright() as p:
#         browser = p.chromium.launch(
#             headless=False,      # ❗ ห้าม headless
#             slow_mo=80           # ❗ ใส่ delay
#         )

#         context = browser.new_context(
#             locale="th-TH",
#             user_agent=(
#                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#                 "AppleWebKit/537.36 (KHTML, like Gecko) "
#                 "Chrome/120.0 Safari/537.36"
#             ),
#             viewport={"width": 1280, "height": 800}
#         )

#         page = context.new_page()
#         page.goto(url, timeout=60000, wait_until="domcontentloaded")

#         # ⏳ รอจริง ๆ
#         time.sleep(5)

#         # 🖱️ scroll เพื่อ trigger job list
#         for _ in range(5):
#             page.mouse.wheel(0, 1500)
#             time.sleep(1)

#         # 🔍 ตอนนี้ค่อย query
#         links = page.query_selector_all("a[href^='/th/job/']")

#         for link in links:
#             title = link.inner_text().strip()
#             href = link.get_attribute("href")

#             if title and href:
#                 jobs.append({
#                     "title": title,
#                     "url": "https://www.jobthai.com" + href,
#                     "source": "jobthai"
#                 })

#         browser.close()

#     print("✅ jobs:", len(jobs))
#     return jobs
