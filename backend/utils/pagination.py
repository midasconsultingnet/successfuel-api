from pydantic import BaseModel


class PaginationResponse(BaseModel):
    skip: int
    limit: int
    total: int