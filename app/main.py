from typing import List
from app.models import Book, User, Review
from sqlalchemy.orm import Session
from app.schemas import BookCreate, Book as BookSchema, ReviewCreate, Review as ReviewSchema
from app.database import engine,SessionLocal, Base
from fastapi import FastAPI, Depends, HTTPException, status, Query
from app.authenticate import router as auth_router, get_current_user

app = FastAPI()

# Include the authentication router
app.include_router(auth_router)

# Database utility
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/books/", response_model=BookSchema, status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_book = Book(**book.model_dump())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@app.get("/books/", response_model=List[BookSchema])
def read_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    books = db.query(Book).offset(skip).limit(limit).all()
    return books

@app.get("/books/{book_id}", response_model=BookSchema)
def read_book(book_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.put("/books/{book_id}", response_model=BookSchema)
def update_book(book_id: int, book: BookCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    db_book.title = book.title
    db_book.author = book.author
    db.commit()
    db.refresh(db_book)
    return db_book

@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(db_book)
    db.commit()
    return {"ok": True}

@app.post("/books/{book_id}/reviews/", response_model=ReviewSchema, status_code=status.HTTP_201_CREATED)
def create_review(book_id: int, review: ReviewCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    db_review = Review(**review.model_dump(), book_id=book_id)
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

@app.get("/books/{book_id}/reviews/", response_model=List[ReviewSchema])
def read_reviews(book_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    reviews = db.query(Review).filter(Review.book_id == book_id).all()
    if not reviews:
        raise HTTPException(status_code=404, detail="No reviews found for this book")
    return reviews

@app.get("/books/search/", response_model=List[BookSchema])
def search_books(
    title: str = Query(None, description="Search by book title"),
    author: str = Query(None, description="Search by author"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Book)
    if title:
        query = query.filter(Book.title.ilike(f"%{title}%"))
    if author:
        query = query.filter(Book.author.ilike(f"%{author}%"))
    
    results = query.all()
    if not results:
        raise HTTPException(status_code=404, detail="No books found matching the criteria")
    return results

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)