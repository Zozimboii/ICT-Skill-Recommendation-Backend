# app/util/trend_utils.py
from collections import Counter
from datetime import date


def summarize_job_title_trend(jobs: list, limit: int = 10):
    """
    รับ list ของ jobs แล้วสรุปจำนวน job ต่อวัน
    """

    counter = Counter()

    for job in jobs:
        # สมมติ job มี field created_date
        snapshot = job.get("snapshot_date", str(date.today()))
        counter[snapshot] += 1

    series = [
        {"snapshot_date": d, "job_count": c} for d, c in counter.most_common(limit)
    ]

    return series
