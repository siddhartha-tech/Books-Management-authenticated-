from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    hashed_password = Column(String)

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String)
    reviews = relationship("Review", back_populates="book")

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True)
    content = Column(Text)
    book_id = Column(Integer, ForeignKey('books.id'))

    book = relationship("Book", back_populates="reviews")
