from ninja import Schema
from typing import Optional


class UserOut(Schema):
    id: int
    email: str
    username: str
    name: Optional[str]
    bio: Optional[str]


class UpdateUserSchema(Schema):
    name: Optional[str] = None
    bio: Optional[str] = None