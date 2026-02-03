'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import toast from 'react-hot-toast'
import { useAuth } from '@/lib/auth-context'
import { api } from '@/lib/api'
import { IconArrowLeft, IconLoader2 } from '@tabler/icons-react'

export default function NewBookPage() {
  const { user, loading } = useAuth()
  const router = useRouter()
  const [title, setTitle] = useState('')
  const [author, setAuthor] = useState('')
  const [genre, setGenre] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [err, setErr] = useState('')
  const [submitting, setSubmitting] = useState(false)

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

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setErr('')
    setSubmitting(true)
    const form = new FormData()
    form.append('title', title)
    if (author) form.append('author', author)
    if (genre) form.append('genre', genre)
    if (file) form.append('file', file)
    try {
      await api.books.create(form)
      toast.success('Book added successfully')
      router.push('/books')
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Failed'
      setErr(msg)
      toast.error(msg)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="max-w-lg">
      <Link href="/books" className="mb-6 inline-flex items-center gap-2 text-sm font-medium text-muted transition hover:text-slate-900">
        <IconArrowLeft className="h-4 w-4" />
        Back to books
      </Link>
      <div className="card">
        <h1 className="page-title mb-6">Add book</h1>
        <form onSubmit={handleSubmit} className="space-y-5">
          {err && (
            <div className="rounded-lg bg-red-50 px-3 py-2 text-error">
              {err}
            </div>
          )}
          <div>
            <label className="label">Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="input-field"
              placeholder="Book title"
              required
            />
          </div>
          <div>
            <label className="label">Author</label>
            <input
              type="text"
              value={author}
              onChange={(e) => setAuthor(e.target.value)}
              className="input-field"
              placeholder="Optional"
            />
          </div>
          <div>
            <label className="label">Genre</label>
            <input
              type="text"
              value={genre}
              onChange={(e) => setGenre(e.target.value)}
              className="input-field"
              placeholder="e.g. Fiction"
            />
          </div>
          <div>
            <label className="label">File (text or PDF)</label>
            <input
              type="file"
              accept=".txt,.pdf"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="input-field file:mr-2 file:rounded-lg file:border-0 file:bg-primary-50 file:px-4 file:py-2 file:text-sm file:font-medium file:text-primary-700 hover:file:bg-primary-100"
            />
          </div>
          <div className="flex flex-wrap gap-3 pt-2">
            <button type="submit" disabled={submitting} className="btn-primary">
              {submitting ? (
                <>
                  <IconLoader2 className="h-4 w-4 animate-spin" />
                  Adding...
                </>
              ) : (
                'Add book'
              )}
            </button>
            <Link href="/books" className="btn-secondary">
              Cancel
            </Link>
          </div>
        </form>
      </div>
    </div>
  )
}
