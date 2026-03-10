# scripts/scrap.py
import sys

from app.model import user, job, skill, transcript, recommendation, ai_model
from app.services.job_scraper_service import JobScraperService


if __name__ == "__main__":
    service = JobScraperService()
    max_jobs = int(sys.argv[1]) if len(sys.argv) > 1 else 10

    print(f"🚀 Starting scrape — target: {max_jobs} new jobs")
    service.run_scraping(max_jobs=max_jobs)