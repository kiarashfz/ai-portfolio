from pydantic import BaseModel


class ChangeCounts(BaseModel):
    draft_count: int
    ready_count: int
    published_count: int
    failed_to_publish_count: int
