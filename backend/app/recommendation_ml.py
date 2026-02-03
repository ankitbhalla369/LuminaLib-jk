from typing import Sequence

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from app.models import Book


def _book_text(b: Book) -> str:
    parts = [b.title or "", b.author or "", b.genre or "", (b.summary or "")[:500]]
    return " ".join(parts).strip() or str(b.id)


def similar_books(
    books: Sequence[Book],
    book_id: int,
    limit: int = 10,
) -> list[tuple[Book, float]]:
    books = list(books)
    if len(books) < 2:
        return []
    idx = next((i for i, b in enumerate(books) if b.id == book_id), None)
    if idx is None:
        return []
    texts = [_book_text(b) for b in books]
    vec = TfidfVectorizer(max_features=200, stop_words="english", min_df=1)
    try:
        X = vec.fit_transform(texts)
    except Exception:
        return []
    sim = cosine_similarity(X[idx : idx + 1], X).ravel()
    order = np.argsort(-sim)
    out = []
    for i in order:
        if i == idx or sim[i] <= 0:
            continue
        out.append((books[i], float(sim[i])))
        if len(out) >= limit:
            break
    return out


def collaborative_scores(
    user_borrowed_ids: set[int],
    all_borrows: list[tuple[int, int]],
    candidate_book_ids: set[int],
) -> dict[int, float]:
    if not user_borrowed_ids or not all_borrows:
        return {bid: 0.0 for bid in candidate_book_ids}
    user_to_books: dict[int, set[int]] = {}
    for uid, bid in all_borrows:
        user_to_books.setdefault(uid, set()).add(bid)
    users_who_borrowed_mine = {
        u for u, bset in user_to_books.items()
        if bset & user_borrowed_ids
    }
    scores = {}
    for bid in candidate_book_ids:
        count = sum(1 for u in users_who_borrowed_mine if bid in user_to_books.get(u, set()))
        scores[bid] = float(count)
    return scores


def build_book_matrix(books: list[Book]):
    if not books:
        return None, None
    texts = [_book_text(b) for b in books]
    vec = TfidfVectorizer(max_features=200, stop_words="english", min_df=1)
    try:
        X = vec.fit_transform(texts)
        return vec, X
    except Exception:
        return None, None


def content_similarity_to_user_books(
    books: list[Book],
    user_borrowed_ids: set[int],
    X,
) -> dict[int, float]:
    if not user_borrowed_ids or X is None or X.shape[0] == 0:
        return {}
    book_id_to_idx = {b.id: i for i, b in enumerate(books)}
    borrowed_idx = [book_id_to_idx[bid] for bid in user_borrowed_ids if bid in book_id_to_idx]
    if not borrowed_idx:
        return {}
    user_vec = np.asarray(X[borrowed_idx].mean(axis=0))
    sims = cosine_similarity(user_vec.reshape(1, -1), X).ravel()
    return {books[i].id: float(sims[i]) for i in range(len(books)) if books[i].id not in user_borrowed_ids}
