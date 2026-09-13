import uuid
from pydantic import BaseModel, ConfigDict

class CategoryBase(BaseModel):
    name: str
    slug: str

class CategoryResponse(CategoryBase):
    id: uuid.UUID
    story_count: int = 0
    model_config = ConfigDict(from_attributes=True)
