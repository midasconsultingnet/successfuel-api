import strawberry
from datetime import datetime
from typing import Optional

@strawberry.type
class BaseGraphQLType:
    id: str
    statut: str
    created_at: datetime
    updated_at: Optional[datetime] = None