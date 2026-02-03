from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db import get_db
from app.models import User, Book, UserPreference, Borrow
from app.config import settings
from app.deps import get_current_user, get_llm
from app.schemas import PreferenceCreate
from app.recommendation_ml import (
    similar_books,
    collaborative_scores,
    content_similarity_to_user_books,
    build_book_matrix,
)
from app.llm.base import LLMBackend

router = APIRouter(tags=["recommendations"])

MAX_BOOKS_FOR_ML = 500
MAX_CANDIDATES_FOR_LLM = 80


def _norm(scores: dict[int, float]) -> dict[int, float]:
    if not scores:
        return scores
    m = max(scores.values()) or 1.0
    return {k: v / m for k, v in scores.items()}


@router.get("/preferences")
async def list_preferences(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(UserPreference.genre, UserPreference.weight).where(UserPreference.user_id == user.id))
    return [{"genre": row[0], "weight": row[1]} for row in r.all()]


@router.post("/preferences")
async def set_preference(
    data: PreferenceCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(UserPreference).where(UserPreference.user_id == user.id, UserPreference.genre == data.genre))
    row = r.scalar_one_or_none()
    if row:
        row.weight = data.weight
    else:
        db.add(UserPreference(user_id=user.id, genre=data.genre, weight=data.weight))
    await db.commit()
    return {"ok": True}


@router.get("/recommendations/suggestions")
async def get_ai_suggestions(
    limit: int = 10,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    llm: LLMBackend = Depends(get_llm),
):
    """AI suggestions for books not necessarily in the catalog, based on genre preferences."""
    prefs = await db.execute(select(UserPreference.genre).where(UserPreference.user_id == user.id))
    genres = [r[0] for r in prefs.all() if r[0]]
    if not genres:
        return {"suggestions": []}
    suggestions = await llm.suggest_books_by_genre(genres, limit=limit)
    return {"suggestions": suggestions}


@router.get("/recommendations/suggestions/similar/{book_id}")
async def get_ai_suggestions_similar_to_book(
    book_id: int,
    limit: int = 6,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    llm: LLMBackend = Depends(get_llm),
):
    """AI suggestions for books similar to the given book (not necessarily in the catalog)."""
    r = await db.execute(select(Book).where(Book.id == book_id))
    book = r.scalar_one_or_none()
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    suggestions = await llm.suggest_books_similar_to(
        book_title=book.title or "",
        book_author=book.author,
        book_genre=book.genre,
        book_summary=book.summary,
        limit=limit,
    )
    return {"suggestions": suggestions}


@router.get("/recommendations")
async def get_recommendations(
    limit: int = 10,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    llm: LLMBackend = Depends(get_llm),
):
    borrowed = await db.execute(select(Borrow.book_id).where(Borrow.user_id == user.id))
    borrowed_ids = {r[0] for r in borrowed.all()}

    books_result = await db.execute(
        select(Book).order_by(Book.created_at.desc()).limit(MAX_BOOKS_FOR_ML)
    )
    books = books_result.scalars().all()
    candidates = [b for b in books if b.id not in borrowed_ids]
    if not candidates:
        return []

    if settings.recommendation_engine == "llm":
        prefs = await db.execute(select(UserPreference).where(UserPreference.user_id == user.id))
        pref_rows = prefs.scalars().all()
        pref_parts = [f"{p.genre} (weight {p.weight})" for p in pref_rows]
        pref_str = "Genres: " + ", ".join(pref_parts) if pref_parts else "No genre preferences set."
        candidate_dicts = [{"id": b.id, "title": b.title or "", "author": b.author or "", "genre": b.genre or ""} for b in candidates[:MAX_CANDIDATES_FOR_LLM]]
        ids = await llm.recommend_for_user(pref_str, candidate_dicts, limit=limit)
        book_by_id = {b.id: b for b in books}
        return [
            {"id": b.id, "title": b.title, "author": b.author, "genre": b.genre}
            for bid in ids if bid in book_by_id
            for b in (book_by_id[bid],)
        ][:limit]

    prefs = await db.execute(select(UserPreference).where(UserPreference.user_id == user.id))
    pref_rows = prefs.scalars().all()
    genre_weights = {p.genre.lower(): p.weight for p in pref_rows} if pref_rows else {}
    candidate_ids = {b.id for b in candidates}

    preference_score: dict[int, float] = {}
    for b in candidates:
        s = 1.0
        if b.genre and b.genre.lower() in genre_weights:
            s += genre_weights[b.genre.lower()]
        preference_score[b.id] = s
    preference_score = _norm(preference_score)

    all_borrows_result = await db.execute(select(Borrow.user_id, Borrow.book_id))
    all_borrows = [(r[0], r[1]) for r in all_borrows_result.all()]
    collab_score = collaborative_scores(borrowed_ids, all_borrows, candidate_ids)
    collab_score = _norm(collab_score)

    _, X = build_book_matrix(books)
    content_score = content_similarity_to_user_books(books, borrowed_ids, X) if X is not None else {}
    content_score = _norm(content_score)

    blended: dict[int, float] = {}
    for bid in candidate_ids:
        p = preference_score.get(bid, 0.0)
        c = collab_score.get(bid, 0.0)
        t = content_score.get(bid, 0.0)
        blended[bid] = 0.4 * p + 0.4 * c + 0.2 * t

    book_by_id = {b.id: b for b in books}
    ordered = sorted(blended.items(), key=lambda x: -x[1])[:limit]
    return [
        {"id": b.id, "title": b.title, "author": b.author, "genre": b.genre}
        for bid, _ in ordered
        for b in (book_by_id.get(bid),)
        if b
    ]


@router.get("/recommendations/similar/{book_id}")
async def get_similar_books(
    book_id: int,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    llm: LLMBackend = Depends(get_llm),
):
    r = await db.execute(select(Book).where(Book.id == book_id))
    book = r.scalar_one_or_none()
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    books_result = await db.execute(select(Book).order_by(Book.created_at.desc()).limit(MAX_BOOKS_FOR_ML))
    books = books_result.scalars().all()
    others = [b for b in books if b.id != book_id]
    if not others:
        return []

    if settings.recommendation_engine == "llm":
        book_info = f"{book.title or ''} by {book.author or ''} ({book.genre or ''}). { (book.summary or '')[:300]}"
        candidate_dicts = [{"id": b.id, "title": b.title or "", "author": b.author or "", "genre": b.genre or ""} for b in others[:MAX_CANDIDATES_FOR_LLM]]
        ids = await llm.recommend_similar(book_info, candidate_dicts, limit=limit)
        book_by_id = {b.id: b for b in books}
        return [
            {"id": bid, "title": book_by_id[bid].title, "author": book_by_id[bid].author, "genre": book_by_id[bid].genre, "score": 1.0}
            for bid in ids if bid in book_by_id
        ][:limit]

    similar = similar_books(books, book_id, limit=limit)
    return [
        {"id": b.id, "title": b.title, "author": b.author, "genre": b.genre, "score": round(s, 4)}
        for b, s in similar
    ]
