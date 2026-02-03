'use client'

import { useState, useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'
import Link from 'next/link'
import toast from 'react-hot-toast'
import { useAuth } from '@/lib/auth-context'
import { api, type BookDetail } from '@/lib/api'
import { BookViewModal } from '@/components/BookViewModal'
import { IconArrowLeft, IconBook2, IconChevronRight, IconEye, IconLoader2, IconSparkles, IconStar } from '@tabler/icons-react'

export default function BookDetailPage() {
  const { user, loading } = useAuth()
  const router = useRouter()
  const params = useParams()
  const id = Number(params.id)
  const [book, setBook] = useState<BookDetail | null>(null)
  const [analysis, setAnalysis] = useState<{ summary: string | null; consensus: string | null } | null>(null)
  const [aiSimilar, setAiSimilar] = useState<{ title: string; author: string; genre: string }[]>([])
  const [loadingAiSimilar, setLoadingAiSimilar] = useState(false)
  const [err, setErr] = useState('')
  const [action, setAction] = useState('')
  const [rating, setRating] = useState(3)
  const [reviewText, setReviewText] = useState('')
  const [viewModalOpen, setViewModalOpen] = useState(false)

  useEffect(() => {
    if (!loading && !user) router.push('/login')
  }, [user, loading, router])

  useEffect(() => {
    if (!user || !id) return
    api.books.get(id)
      .then(setBook)
      .catch((e) => setErr(e instanceof Error ? e.message : 'Failed'))
    api.books.analysis(id).then(setAnalysis).catch(() => setAnalysis(null))
    setLoadingAiSimilar(true)
    api.recommendations.suggestionsSimilar(id, 3)
      .then((r) => setAiSimilar(r.suggestions || []))
      .catch(() => setAiSimilar([]))
      .finally(() => setLoadingAiSimilar(false))
  }, [user, id])

  async function doBorrow() {
    setAction('borrowing')
    setErr('')
    try {
      await api.books.borrow(id)
      setAction('')
      const updated = await api.books.get(id)
      setBook(updated)
      toast.success('Book borrowed successfully')
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Failed'
      setErr(msg)
      setAction('')
      toast.error(msg)
    }
  }

  async function doReturn() {
    setAction('returning')
    setErr('')
    try {
      await api.books.return(id)
      setAction('')
      const updated = await api.books.get(id)
      setBook(updated)
      toast.success('Book returned successfully')
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Failed'
      setErr(msg)
      setAction('')
      toast.error(msg)
    }
  }

  async function doReview(e: React.FormEvent) {
    e.preventDefault()
    setAction('reviewing')
    setErr('')
    try {
      await api.books.review(id, rating, reviewText || undefined)
      setAction('')
      setReviewText('')
      const updated = await api.books.get(id)
      setBook(updated)
      const analysisData = await api.books.analysis(id)
      setAnalysis(analysisData)
      setTimeout(() => {
        api.books.analysis(id).then(setAnalysis).catch(() => {})
      }, 3000)
      toast.success('Review submitted')
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Failed'
      setErr(msg)
      setAction('')
      toast.error(msg)
    }
  }

  if (loading || !user) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <span className="flex items-center gap-2 text-muted">
          <IconLoader2 className="h-5 w-5 animate-spin" />
          Loading...
        </span>
      </div>
    )
  }
  if (!book) {
    return (
      <div className="card">
        <p className="text-error">{err || 'Loading...'}</p>
        <Link href="/books" className="btn-secondary mt-4 inline-flex items-center gap-2">
          <IconArrowLeft className="h-4 w-4" />
          Back to books
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <Link href="/books" className="inline-flex items-center gap-2 text-sm font-medium text-muted transition hover:text-slate-900">
        <IconArrowLeft className="h-4 w-4" />
        Back to books
      </Link>
      <div className="card">
        <div className="flex gap-4">
          <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-xl bg-primary-100">
            <IconBook2 className="h-8 w-8 text-primary-600" />
          </div>
          <div className="min-w-0 flex-1">
            <h1 className="page-title mb-1">{book.title}</h1>
            {book.author && <p className="text-muted mb-2">{book.author}</p>}
            {book.genre && (
              <span className="inline-block rounded-full bg-primary-50 px-2.5 py-0.5 text-xs font-medium text-primary-700">
                {book.genre}
              </span>
            )}
          </div>
        </div>
      </div>
      {err && (
        <div className="rounded-lg bg-red-50 px-4 py-3 text-error">
          {err}
        </div>
      )}
      <div className="flex flex-wrap gap-3">
        <button
          onClick={doBorrow}
          disabled={!!action || book.currently_borrowed_by_me}
          className="btn-primary"
          aria-label={book.currently_borrowed_by_me ? 'Already borrowed' : 'Borrow'}
        >
          {action === 'borrowing' ? (
            <>
              <IconLoader2 className="h-4 w-4 animate-spin" />
              Borrowing...
            </>
          ) : (
            'Borrow'
          )}
        </button>
        <button
          onClick={doReturn}
          disabled={!!action || !book.currently_borrowed_by_me}
          className="btn-secondary"
          aria-label={!book.currently_borrowed_by_me ? 'Not borrowed' : 'Return'}
        >
          {action === 'returning' ? (
            <>
              <IconLoader2 className="h-4 w-4 animate-spin" />
              Returning...
            </>
          ) : (
            'Return'
          )}
        </button>
        {book.file_name && (
          <button
            type="button"
            onClick={() => setViewModalOpen(true)}
            className="btn-secondary inline-flex items-center gap-2"
          >
            <IconEye className="h-4 w-4" />
            View
          </button>
        )}
      </div>
      <BookViewModal
        open={viewModalOpen}
        onClose={() => setViewModalOpen(false)}
        bookId={id}
        bookTitle={book.title}
        fileName={book.file_name}
      />
      {(loadingAiSimilar || aiSimilar.length > 0) && (
        <div className="card space-y-4">
          <h2 className="font-semibold text-slate-900 flex items-center gap-2">
            <IconSparkles className="h-5 w-5 text-primary-600" />
            Similar books (AI suggestions)
          </h2>
          <p className="text-sm text-muted">Books you might also like, based on this one. These may not be in the catalog.</p>
          {loadingAiSimilar ? (
            <div className="flex min-h-[120px] items-center justify-center py-8">
              <span className="flex items-center gap-2 text-muted">
                <IconLoader2 className="h-6 w-6 animate-spin" />
                Loading similar books...
              </span>
            </div>
          ) : (
            <ul className="grid gap-3 sm:grid-cols-2 lg:grid-cols-1">
              {aiSimilar.map((s, i) => (
                <li key={`${s.title}-${i}`} className="card flex items-center gap-4">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary-100">
                    <IconBook2 className="h-5 w-5 text-primary-600" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <h3 className="font-semibold text-slate-900 truncate">{s.title}</h3>
                    <p className="text-sm text-muted">{s.author}</p>
                    {s.genre && (
                      <span className="mt-1 inline-block rounded-full bg-primary-50 px-2 py-0.5 text-xs font-medium text-primary-700">
                        {s.genre}
                      </span>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
      {analysis && (analysis.summary || analysis.consensus) && (
        <div className="card space-y-4">
          <h2 className="font-semibold text-slate-900">Insights</h2>
          {analysis.summary && (
            <div>
              <p className="label text-slate-600">Summary</p>
              <p className="text-slate-700">{analysis.summary}</p>
            </div>
          )}
          {analysis.consensus && (
            <div>
              <p className="label text-slate-600">Review consensus</p>
              <p className="text-slate-700">{analysis.consensus}</p>
            </div>
          )}
        </div>
      )}
      <div className="card">
        <h2 className="font-semibold text-slate-900 mb-1">Leave a review</h2>
        {!book.can_review ? (
          <p className="text-sm text-muted">
            You must borrow this book before you can leave a review. Use the Borrow button above.
          </p>
        ) : book.my_review ? (
          <div className="space-y-3">
            <p className="label flex items-center gap-2 text-slate-600">
              <IconStar className="h-4 w-4" />
              Your rating
            </p>
            <p className="text-slate-800">{book.my_review.rating} / 5</p>
            {book.my_review.text && (
              <>
                <p className="label text-slate-600">Your comment</p>
                <p className="rounded-lg border border-surface-border bg-surface-muted/30 px-3 py-2.5 text-slate-700 whitespace-pre-wrap">
                  {book.my_review.text}
                </p>
              </>
            )}
          </div>
        ) : (
          <>
            <form onSubmit={doReview} className="space-y-4">
              <div>
                <label className="label flex items-center gap-2">
                  <IconStar className="h-4 w-4" />
                  Rating (1–5)
                </label>
                <select
                  value={rating}
                  onChange={(e) => setRating(Number(e.target.value))}
                  className="input-field max-w-[8rem]"
                >
                  {[1, 2, 3, 4, 5].map((n) => (
                    <option key={n} value={n}>{n}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="label">Comment</label>
                <textarea
                  value={reviewText}
                  onChange={(e) => setReviewText(e.target.value)}
                  className="input-field resize-none"
                  rows={3}
                  placeholder="Share your thoughts..."
                />
              </div>
              <button type="submit" disabled={!!action} className="btn-primary">
                {action === 'reviewing' ? (
                  <>
                    <IconLoader2 className="h-4 w-4 animate-spin" />
                    Submitting...
                  </>
                ) : (
                  'Submit review'
                )}
              </button>
            </form>
          </>
        )}
      </div>
    </div>
  )
}
