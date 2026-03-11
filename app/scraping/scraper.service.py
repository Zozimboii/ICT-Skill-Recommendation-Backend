# app/services/scraper_service.py
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time
import re

class ScraperService:

    BASE_URL = "https://th.jobsdb.com/th/jobs-in-information-communication-technology"

    def fetch_job_list_page(self,page: int = 1):
        url = f"{self.BASE_URL}?page={page}"
        with sync_playwright() as p:
            
            browser = p.chromium.launch(headless=True)
  
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            )
            page = context.new_page()

            page.goto(url)

            # รอให้ job โหลด (สำคัญมาก)
            page.wait_for_selector("article[data-automation='normalJob']")

            html = page.content()

            browser.close()

        return html

    def parse_job_list(self, html: str):

        soup = BeautifulSoup(html, "html.parser")
        jobs = []

        job_cards = soup.select("article[data-automation='normalJob']")

        for card in job_cards:

            # title
            title_tag = card.select_one("a[data-automation='jobTitle']")
            title = title_tag.text.strip() if title_tag else ""

            # detail link
            detail_url = ""
            if title_tag:
                href = title_tag.get("href")
                detail_url = href if href.startswith("http") \
                    else f"https://th.jobsdb.com{href}"

            # company
            company_tag = card.select_one("a[data-automation='jobCompany']")
            company = company_tag.text.strip() if company_tag else ""

            # location
            location_tag = card.select_one("a[data-automation='jobLocation']")
            location = location_tag.text.strip() if location_tag else ""

            # salary
            salary_tag = card.select_one("span[data-automation='jobSalary']")
            salary_text = salary_tag.text.strip() if salary_tag else ""

            salary_min = None
            salary_max = None

            if salary_text:
                numbers = re.findall(r"\d[\d,]*", salary_text)
                if len(numbers) >= 1:
                    salary_min = int(numbers[0].replace(",", ""))
                if len(numbers) >= 2:
                    salary_max = int(numbers[1].replace(",", ""))

            if not detail_url:
                continue

            jobs.append({
                "title": title,
                "company_name": company,
                "location": location,
                "salary_min": salary_min,
                "salary_max": salary_max,
                "detail_url": detail_url
            })

        return jobs

    def fetch_job_detail(self, url: str):
        from playwright.sync_api import sync_playwright

        posted_text = None
        description = ""

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)  
            context = browser.new_context()
            page = context.new_page()

            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)

                try:
                    locator = page.locator("text=ลงประกาศ")
                    if locator.count() > 0:
                        posted_text = locator.first.inner_text().strip()
                except:
                    posted_text = None

                if not posted_text:
                    try:
                        locator = page.locator("text=ago")
                        if locator.count() > 0:
                            posted_text = locator.first.inner_text().strip()
                    except:
                        posted_text = None

                try:
                    desc_locator = page.locator('[data-automation="jobAdDetails"]')
                    if desc_locator.count() > 0:
                        description = desc_locator.first.inner_text()
                except:
                    description = ""

            except Exception as e:
                print("ERROR:", e)

            finally:
                browser.close()

        print("DEBUG POSTED:", posted_text)

        return {
            "description": description.strip(),
            "posted_text": posted_text
        }