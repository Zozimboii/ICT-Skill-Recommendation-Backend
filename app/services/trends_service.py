# backend/app/services/trends_service.py
# from datetime import datetime
# from app.scrapers.jobsdb_scapper import fetch_jobsdb

# def jobsdb_trend(limit: int = 20):
#     jobs = fetch_jobsdb()
#     items = summarize_job_title_trend(jobs, limit)

#     return {
#         "source": "JobsDB",
#         "metric": "job_title_frequency",
#         "as_of": datetime.utcnow().isoformat(),
#         "items": items,
#     }

# from app.utils.trend_utils import summarize_job_title_trend


# def jobsdb_trend(days: int = 30, limit: int = 10):
#     jobs = []

#     items = summarize_job_title_trend(jobs, limit)

#     return {"series": items}

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models import JobCountHistory


def jobsdb_trend(db: Session, days: int = 30):
    # รวม job_count ของทุก sub_category ในวันเดียวกัน
    rows = (
        db.query(
            JobCountHistory.snapshot_date,
            func.sum(JobCountHistory.job_count).label("total_count"),
        )
        .group_by(JobCountHistory.snapshot_date)
        .order_by(JobCountHistory.snapshot_date.asc())  # เรียงจากเก่าไปใหม่สำหรับวาดกราฟ
        .limit(days)
        .all()
    )

    return {
        "series": [
            {"snapshot_date": str(r.snapshot_date), "job_count": int(r.total_count)}
            for r in rows
        ]
    }
