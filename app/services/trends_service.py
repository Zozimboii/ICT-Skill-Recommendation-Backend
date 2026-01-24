# backend/app/services/trends_service.py
from datetime import datetime
from app.scrapers.jobsdb_scapper import fetch_jobsdb, summarize_job_title_trend

def jobsdb_trend(limit: int = 20):
    jobs = fetch_jobsdb()
    items = summarize_job_title_trend(jobs, limit)

    return {
        "source": "JobsDB",
        "metric": "job_title_frequency",
        "as_of": datetime.utcnow().isoformat(),
        "items": items,
    }
