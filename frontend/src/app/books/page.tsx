'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '@/lib/auth-context'
import { api, type Book } from '@/lib/api'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { ErrorMessage } from '@/components/ErrorMessage'
import { BookCard } from '@/components/BookCard'
import { IconPlus, IconBook2, IconChevronLeft, IconChevronRight } from '@tabler/icons-react'

const PAGE_SIZE = 20

export default function BooksPage() {
  const { user, loading } = useAuth()
  const router = useRouter()
  const [books, setBooks] = useState<Book[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(0)
  const [err, setErr] = useState('')
  const [loadingBooks, setLoadingBooks] = useState(true)

  useEffect(() => {
    if (!loading && !user) router.push('/login')
  }, [user, loading, router])

  useEffect(() => {
    if (!user) return
    setLoadingBooks(true)
    setErr('')
    api.books
      .list(page * PAGE_SIZE, PAGE_SIZE)
      .then((res) => {
        setBooks(res.items)
        setTotal(res.total)
      })
      .catch((e) => setErr(e instanceof Error ? e.message : 'Failed to load'))
      .finally(() => setLoadingBooks(false))
  }, [user, page])

  if (loading || !user) {
    return <LoadingSpinner message="Loading..." className="min-h-[40vh]" />
  }

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))
  const hasPrev = page > 0
  const hasNext = page < totalPages - 1

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <h1 className="page-title">Books</h1>
        <Link href="/books/new" className="btn-primary inline-flex items-center gap-2 sm:ml-auto">
          <IconPlus className="h-4 w-4" />
          Add book
        </Link>
      </div>
      <ErrorMessage message={err} />
      {loadingBooks && books.length === 0 && <LoadingSpinner message="Loading books..." />}
      {!loadingBooks && books.length === 0 && !err && (
        <div className="card text-center py-12">
          <IconBook2 className="mx-auto h-12 w-12 text-slate-300 mb-4" />
          <p className="text-muted mb-4">No books yet.</p>
          <Link href="/books/new" className="btn-primary inline-flex items-center gap-2">
            <IconPlus className="h-4 w-4" />
            Add your first book
          </Link>
        </div>
      )}
      {books.length > 0 && (
        <>
          <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-1">
            {books.map((b) => (
              <BookCard key={b.id} book={b} />
            ))}
          </ul>
          {totalPages > 1 && (
            <nav
              className="flex items-center justify-between border-t border-slate-200 pt-4"
              aria-label="Books pagination"
            >
              <p className="text-sm text-muted">
                Page {page + 1} of {totalPages} ({total} books)
              </p>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => setPage((p) => p - 1)}
                  disabled={!hasPrev}
                  className="btn-secondary inline-flex items-center gap-1 disabled:opacity-50 disabled:pointer-events-none"
                  aria-label="Previous page"
                >
                  <IconChevronLeft className="h-4 w-4" />
                  Previous
                </button>
                <button
                  type="button"
                  onClick={() => setPage((p) => p + 1)}
                  disabled={!hasNext}
                  className="btn-secondary inline-flex items-center gap-1 disabled:opacity-50 disabled:pointer-events-none"
                  aria-label="Next page"
                >
                  Next
                  <IconChevronRight className="h-4 w-4" />
                </button>
              </div>
            </nav>
          )}
        </>
      )}
    </div>
  )
}
