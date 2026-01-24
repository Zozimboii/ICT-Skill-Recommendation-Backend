from playwright.sync_api import sync_playwright
import time
from collections import Counter

def fetch_jobsdb():
    """
    Fetch REAL jobs from JobsDB using pagination (correct way)
    + show job titles with real counts
    """
    base_url = "https://th.jobsdb.com/th/jobs"

    jobs = {}  # ใช้ link เป็น unique key

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            locale="th-TH",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            )
        )

        page = context.new_page()
        page_no = 1

        while True:
            url = f"{base_url}?page={page_no}"
            print(f"🔍 Visiting page {page_no}")

            try:
                page.goto(url, timeout=60000)
                page.wait_for_timeout(3000)

                job_elements = page.query_selector_all(
                    "a[data-automation='jobTitle']"
                )

                if not job_elements:
                    print("🛑 No jobs found — stop pagination")
                    break

                new_count = 0

                for el in job_elements:
                    title = el.inner_text().strip()
                    link = el.get_attribute("href")

                    if not title or not link:
                        continue

                    full_link = "https://th.jobsdb.com" + link.split("?")[0]

                    if full_link not in jobs:
                        jobs[full_link] = {
                            "title": title,
                            "source": "jobsdb",
                            "link": full_link
                        }
                        new_count += 1

                print(f"📄 Found {len(job_elements)} jobs | New: {new_count}")

                if new_count == 0:
                    print("🛑 No new jobs — stopping")
                    break

                page_no += 1
                time.sleep(2)

            except Exception as e:
                print(f"⚠️ Failed page {page_no}: {e}")
                break

        browser.close()

    # =======================
    # 📊 SUMMARY SECTION
    # =======================
    titles = [job["title"] for job in jobs.values()]
    counter = Counter(titles)

    print("\n" + "=" * 80)
    print(f"✅ JobsDB scraped (REAL unique): {len(jobs)} jobs")
    print("📌 Job titles & REAL counts")
    print("-" * 80)

    for title, count in counter.most_common():
        print(f"{title:<65} {count}")

    return list(jobs.values())

def summarize_job_title_trend(jobs: list[dict], limit: int = 20):
    titles = [job["title"] for job in jobs if job.get("title")]
    counter = Counter(titles)

    return [
        {"label": title, "count": count}
        for title, count in counter.most_common(limit)
    ]