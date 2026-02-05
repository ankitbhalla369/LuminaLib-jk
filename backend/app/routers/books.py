import uuid
from io import BytesIO
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse, Response
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import User, Book, Borrow, Review, BookSummary, ReviewAnalysis
from app.schemas import (
    BookCreate,
    BookDetailResponse,
    BookListResponse,
    BookResponse,
    BookUpdate,
    MyReviewResponse,
    ReviewCreate,
    ReviewResponse,
)
from app.deps import get_current_user, get_optional_user, get_storage, get_llm

router = APIRouter(prefix="/books", tags=["books"])


def _extract_text_for_summary(content: bytes, filename: str | None) -> str | None:
    """Extract plain text from file content for LLM summarization. Returns None if not usable."""
    if not content or len(content) < 50:
        return None
    ext = (filename or "").split(".")[-1].lower() if "." in (filename or "") else ""
    if ext == "pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(BytesIO(content))
            parts = []
            for page in reader.pages[:50]:  # limit pages
                t = page.extract_text()
                if t:
                    parts.append(t)
            text = "\n".join(parts).strip()[:12000]
            if not text or text.startswith("%PDF") or len(text) < 100:
                return None
            return text
        except Exception:
            return None
    try:
        text = content.decode("utf-8", errors="ignore").strip()[:8000]
        if not text or text.startswith("%PDF"):
            return None
        return text
    except Exception:
        return None


def _run_summary_task(book_id: int, text: str):
    import asyncio
    import threading
    from app.db import SessionLocal
    from app.config import settings
    from app.llm.mock import MockLLM
    from app.llm.ollama import OllamaLLM

    async def _run():
        llm = OllamaLLM() if settings.llm_provider == "ollama" else MockLLM()
        summary_text = await llm.summarize(text)
        async with SessionLocal() as db:
            from app.models import BookSummary, Book
            r = await db.execute(select(BookSummary).where(BookSummary.book_id == book_id))
            row = r.scalar_one_or_none()
            if row:
                row.content = summary_text
            else:
                row = BookSummary(book_id=book_id, content=summary_text)
                db.add(row)
            r3 = await db.execute(select(Book).where(Book.id == book_id))
            book = r3.scalar_one()
            book.summary = summary_text
            await db.commit()

    def run():
        asyncio.run(_run())
    threading.Thread(target=run, daemon=True).start()


def _run_sentiment_task(book_id: int, review_texts: list[str]):
    import asyncio
    import threading
    from app.db import SessionLocal
    from app.config import settings
    from app.llm.mock import MockLLM
    from app.llm.ollama import OllamaLLM

    async def _run():
        llm = OllamaLLM() if settings.llm_provider == "ollama" else MockLLM()
        consensus = await llm.analyze_sentiment(review_texts)
        async with SessionLocal() as db:
            from app.models import ReviewAnalysis
            r = await db.execute(select(ReviewAnalysis).where(ReviewAnalysis.book_id == book_id))
            row = r.scalar_one_or_none()
            if row:
                row.consensus = consensus
            else:
                row = ReviewAnalysis(book_id=book_id, consensus=consensus)
                db.add(row)
            await db.commit()

    def run():
        asyncio.run(_run())
    threading.Thread(target=run, daemon=True).start()


@router.post("", response_model=BookResponse)
async def create_book(
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    author: str = Form(None),
    genre: str = Form(None),
    file: UploadFile = File(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    storage=Depends(get_storage),
):
    file_path = None
    file_name = None
    content = b""
    if file and file.filename:
        ext = file.filename.split(".")[-1] if "." in file.filename else "bin"
        key = f"books/{uuid.uuid4().hex}.{ext}"
        content = await file.read()
        await storage.put(key, BytesIO(content))
        file_path = key
        file_name = file.filename

    book = Book(
        title=title,
        author=author or None,
        genre=genre or None,
        file_path=file_path,
        file_name=file_name,
        added_by_user_id=user.id,
    )
    db.add(book)
    await db.commit()
    await db.refresh(book)

    if file_path and content:
        text = _extract_text_for_summary(content, file_name)
        if text:
            background_tasks.add_task(_run_summary_task, book.id, text)

    return book


@router.get("", response_model=BookListResponse)
async def list_books(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    limit = min(max(1, limit), 100)
    total_r = await db.execute(select(func.count(Book.id)))
    total = total_r.scalar() or 0
    r = await db.execute(
        select(Book).offset(skip).limit(limit).order_by(Book.created_at.desc())
    )
    items = r.scalars().all()
    return BookListResponse(items=items, total=total, skip=skip, limit=limit)


@router.get("/{book_id}", response_model=BookDetailResponse)
async def get_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    r = await db.execute(select(Book).where(Book.id == book_id))
    book = r.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    currently_borrowed_by_me = False
    can_review = False
    my_review = None
    if user:
        r2 = await db.execute(
            select(Borrow).where(
                Borrow.book_id == book_id,
                Borrow.user_id == user.id,
                Borrow.returned_at.is_(None),
            )
        )
        currently_borrowed_by_me = r2.scalar_one_or_none() is not None
        can_review = currently_borrowed_by_me  # true only when currently borrowed (no returned_at)
        r_review = await db.execute(
            select(Review).where(Review.book_id == book_id, Review.user_id == user.id).limit(1)
        )
        review_row = r_review.scalars().first()
        if review_row:
            my_review = MyReviewResponse(rating=review_row.rating, text=review_row.text)
    return BookDetailResponse(
        id=book.id,
        title=book.title,
        author=book.author,
        genre=book.genre,
        summary=book.summary,
        created_at=book.created_at,
        currently_borrowed_by_me=currently_borrowed_by_me,
        can_review=can_review,
        file_name=book.file_name,
        my_review=my_review,
    )


@router.get("/{book_id}/file")
async def get_book_file(
    book_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    storage=Depends(get_storage),
):
    """Return the uploaded book file (text or PDF) for viewing. Requires auth."""
    r = await db.execute(select(Book).where(Book.id == book_id))
    book = r.scalar_one_or_none()
    if not book or not book.file_path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book or file not found")
    content = await storage.get(book.file_path)
    if not content:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    file_name = book.file_name or "file"
    ext = file_name.split(".")[-1].lower() if "." in file_name else ""
    media_type = "application/pdf" if ext == "pdf" else "text/plain"
    return Response(content=content, media_type=media_type, headers={"Content-Disposition": f'inline; filename="{file_name}"'})


@router.put("/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: int,
    data: BookUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(Book).where(Book.id == book_id))
    book = r.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    if data.title is not None:
        book.title = data.title
    if data.author is not None:
        book.author = data.author
    if data.genre is not None:
        book.genre = data.genre
    await db.commit()
    await db.refresh(book)
    return book


@router.delete("/{book_id}")
async def delete_book(
    book_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    storage=Depends(get_storage),
):
    r = await db.execute(select(Book).where(Book.id == book_id))
    book = r.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    if book.file_path:
        await storage.delete(book.file_path)
    await db.delete(book)
    await db.commit()
    return {"ok": True}


@router.post("/{book_id}/borrow")
async def borrow_book(
    book_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(Book).where(Book.id == book_id))
    book = r.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    r2 = await db.execute(
        select(Borrow).where(Borrow.book_id == book_id, Borrow.user_id == user.id, Borrow.returned_at.is_(None))
    )
    if r2.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already borrowed")
    borrow = Borrow(user_id=user.id, book_id=book_id)
    db.add(borrow)
    await db.commit()
    return {"ok": True}


@router.post("/{book_id}/return")
async def return_book(
    book_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from datetime import datetime
    r = await db.execute(
        select(Borrow).where(Borrow.book_id == book_id, Borrow.user_id == user.id, Borrow.returned_at.is_(None))
    )
    borrow = r.scalar_one_or_none()
    if not borrow:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active borrow for this book")
    borrow.returned_at = datetime.utcnow()
    await db.commit()
    return {"ok": True}


@router.post("/{book_id}/reviews", response_model=ReviewResponse)
async def create_review(
    book_id: int,
    data: ReviewCreate,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(
        select(Borrow).where(Borrow.book_id == book_id, Borrow.user_id == user.id)
    )
    borrowed = r.scalars().first()
    if not borrowed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Must borrow book before reviewing")
    if data.rating < 1 or data.rating > 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rating must be 1-5")
    review = Review(user_id=user.id, book_id=book_id, rating=data.rating, text=data.text)
    db.add(review)
    await db.commit()
    await db.refresh(review)

    r2 = await db.execute(select(Review).where(Review.book_id == book_id))
    all_reviews = r2.scalars().all()
    texts = [r.text or f"Rating: {r.rating}" for r in all_reviews if r.text or r.rating]
    if texts:
        background_tasks.add_task(_run_sentiment_task, book_id, texts)

    return review


@router.get("/{book_id}/analysis")
async def get_analysis(book_id: int, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Book).where(Book.id == book_id))
    book = r.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    r2 = await db.execute(select(ReviewAnalysis).where(ReviewAnalysis.book_id == book_id))
    ra = r2.scalar_one_or_none()
    return {"summary": book.summary, "consensus": ra.consensus if ra else None}
