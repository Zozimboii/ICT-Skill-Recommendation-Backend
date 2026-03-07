# schemas/search.py

from pydantic import BaseModel

class SearchJobSummary(BaseModel):
    sub_category_id: int
    sub_category_name: str
    job_count: int

