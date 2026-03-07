# from datetime import date
# from fastapi import APIRouter, Depends
# from requests import Session
# from app.db.models import JobSnapshot

# from backend.app.core.database import get_db

# router = APIRouter()

# @router.post("/test-insert")
# def test_insert(db: Session = Depends(get_db)):
#     sample = JobSnapshot(
#         job_id=1,
#         job_title="Backend Developer",
#         sub_category_id=10,
#         sub_category_name="Developer",
#         company_name="Test Co",
#         snapshot_date=date.today()
#     )

#     db.add(sample)
#     db.commit()

#     return {"status": "inserted"}