from pydantic import BaseModel
from typing import List

class Link(BaseModel):
    id: int
    text: str
    url: str

class ContentRequest(BaseModel):
    inner_text: str
    links: List[Link]

class UserQuery(BaseModel):
    query: str
