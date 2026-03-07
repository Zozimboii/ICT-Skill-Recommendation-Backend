
import sys

import app.model

from app.services.job_service import JobService

if __name__ == "__main__":
    service = JobService()
    max_jobs = int(sys.argv[1]) if len(sys.argv) > 1 else 50

    print(f"🚀 Starting scrape — target: {max_jobs} new jobs")
    service.run_scraping(max_jobs=max_jobs)