from pydantic import BaseModel
from typing import List

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    class Config:
        orm_mode = True

class BookBase(BaseModel):
    title: str
    author: str

class BookCreate(BookBase):
    pass

# Include Review schema for nested serialization
class ReviewBase(BaseModel):
    content: str

class ReviewCreate(ReviewBase):
    pass

class Review(ReviewBase):
    id: int
    book_id: int
    class Config:
        orm_mode = True

class Book(BookBase):
    id: int
    reviews: List[Review] = []  # Define reviews with explicit type

    class Config:
        orm_mode = True
