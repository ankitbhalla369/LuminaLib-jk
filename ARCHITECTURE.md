# LuminaLib Architecture

## Database schema – user preferences

User preferences drive the recommendation engine. The `user_preferences` table stores per-user genre weights: `user_id`, `genre`, and `weight`. A higher weight means the user prefers that genre more. Recommendations score books by matching book genre to these weights; books the user has already borrowed are excluded. This keeps the schema small and makes it easy to add more preference dimensions later (e.g. author, decade) by adding columns or tables and updating the scoring logic.

## Async LLM usage

Book summarization and review sentiment run in background so the API can respond immediately. On book upload, the handler saves the book and file, then starts a background task that decodes the file content, calls the LLM (mock or Ollama), and writes the result to `book_summaries` and the book’s `summary` field. For reviews, submitting a review triggers a background task that loads all reviews for that book, calls the LLM to produce a consensus, and updates `review_analyses`. Both tasks run in a separate thread and use a new async session so they don’t block the request or share the request’s DB session. Swapping the LLM (e.g. mock vs Ollama) is done via config (`LLM_PROVIDER`); the rest of the code uses the shared `LLMBackend` interface.

## Recommendation model (ML-style hybrid)

Recommendations use a **hybrid** of three signals, blended with weights 0.4 / 0.4 / 0.2:

1. **Preference-based (content):** User’s genre weights from `user_preferences`. Each candidate book gets a score from its genre weight; normalized to [0, 1].
2. **Collaborative:** “Users who borrowed what you borrowed also borrowed this.” For each candidate book we count how many users borrowed it who also borrowed at least one book the current user borrowed. Score is that count, normalized.
3. **Content similarity:** TF-IDF on book title, author, genre, and summary (scikit-learn `TfidfVectorizer`). We build a centroid from the user’s borrowed books and score each candidate by cosine similarity to that centroid; normalized.

Candidates are limited to recent books (up to 500); books already borrowed by the user are excluded. Final score = 0.4×preference + 0.4×collaborative + 0.2×content. Results are sorted by this score and limited to the requested size.

**Similar books:** `GET /recommendations/similar/{book_id}` returns books most similar to a given book. With `RECOMMENDATION_ENGINE=llm` the LLM (Llama 3) ranks candidates by similarity; with `RECOMMENDATION_ENGINE=hybrid` (default) TF-IDF + cosine similarity is used (scikit-learn). No separate training step—computed on demand.

**Llama 3 for recommendations:** Set `RECOMMENDATION_ENGINE=llm` in `.env` to use the same LLM (Ollama/Llama 3) for both personalized recommendations and similar books. The LLM receives book/user context and a candidate list and returns an ordered list of book IDs. No scikit-learn is used in that mode. Use `hybrid` for the ML blend (preference + collaborative + TF-IDF) or `llm` for LLM-only ranking.

## Extensibility (single-config swap)

- **Storage:** The app uses a `StorageBackend` interface; the concrete implementation is chosen by `STORAGE_BACKEND` in config. Set `STORAGE_BACKEND=local` for local disk (default) or `STORAGE_BACKEND=s3` for AWS S3 (requires `AWS_BUCKET`, `AWS_REGION`, and credentials). Adding a new backend (e.g. MinIO) is one new class plus one branch in `get_storage()`.
- **LLM:** The app uses an `LLMBackend` interface; the implementation is chosen by `LLM_PROVIDER`. Set `LLM_PROVIDER=mock` (default) or `LLM_PROVIDER=ollama` for local Ollama. Adding OpenAI is one new class (e.g. `OpenAILLM`) implementing `summarize`, `analyze_sentiment`, `recommend_for_user`, `recommend_similar`, `suggest_books_by_genre` plus one branch in `get_llm()` and the corresponding config/env (e.g. `OPENAI_API_KEY`). No change to routers or business logic.

## Frontend choices

- **Framework:** Next.js App Router for routing and SSR where useful (e.g. home page, SEO). Auth-gated pages use client components and `useEffect` to redirect unauthenticated users.
- **State:** No global store. Auth state lives in React Context (`AuthProvider`). List/detail data is fetched in the page or component that needs it and stored in local `useState`; no shared cache layer.
- **Network:** All API calls go through a single `api` object in `src/lib/api.ts`. Components never call `fetch` directly; they use `api.auth.*`, `api.books.*`, etc. So changing base URL or adding interceptors happens in one place.
- **Components:** Pages are composed from reusable components (e.g. `LoadingSpinner`, `ErrorMessage`, `BookCard`, `Nav`) to avoid monolithic page components.
- **Styling:** Tailwind CSS. No CSS modules or styled-components; class names are written in JSX. Layout is responsive (max-width container, stacked on small screens).
- **Errors:** Failed API calls throw; callers use try/catch and set an error message in state, rendered via `ErrorMessage` or inline. The App Router `error.tsx` acts as an error boundary and shows a fallback UI with "Try again" on render errors.
