from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class BookCreate(BaseModel):
    title: str
    author: Optional[str] = None
    genre: Optional[str] = None


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    genre: Optional[str] = None


class BookResponse(BaseModel):
    id: int
    title: str
    author: Optional[str] = None
    genre: Optional[str] = None
    summary: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MyReviewResponse(BaseModel):
    rating: int
    text: Optional[str] = None


class BookDetailResponse(BookResponse):
    currently_borrowed_by_me: bool = False
    can_review: bool = False  # True if user has ever borrowed this book (required to review)
    file_name: Optional[str] = None  # Original filename if book has uploaded file (e.g. .txt, .pdf)
    my_review: Optional[MyReviewResponse] = None  # Current user's review if they have submitted one


class BookListResponse(BaseModel):
    items: list[BookResponse]
    total: int
    skip: int
    limit: int


class ReviewCreate(BaseModel):
    rating: int
    text: Optional[str] = None


class ReviewResponse(BaseModel):
    id: int
    user_id: int
    book_id: int
    rating: int
    text: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PreferenceCreate(BaseModel):
    genre: str
    weight: float = 1.0


class AnalysisResponse(BaseModel):
    summary: Optional[str] = None
    consensus: Optional[str] = None
