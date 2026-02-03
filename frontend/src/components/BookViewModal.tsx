'use client'

import { useState, useEffect, useCallback } from 'react'
import { api } from '@/lib/api'
import { IconX, IconChevronLeft, IconChevronRight, IconLoader2 } from '@tabler/icons-react'

const CHARS_PER_PAGE = 2500

function splitTextIntoPages(text: string): string[] {
  const pages: string[] = []
  let start = 0
  while (start < text.length) {
    let end = Math.min(start + CHARS_PER_PAGE, text.length)
    if (end < text.length) {
      const lastNewline = text.lastIndexOf('\n', end)
      if (lastNewline > start) end = lastNewline + 1
      else {
        const lastSpace = text.lastIndexOf(' ', end)
        if (lastSpace > start) end = lastSpace + 1
      }
    }
    pages.push(text.slice(start, end))
    start = end
  }
  return pages.length ? pages : ['']
}

type BookViewModalProps = {
  open: boolean
  onClose: () => void
  bookId: number
  bookTitle: string
  fileName: string | null | undefined
}

export function BookViewModal({ open, onClose, bookId, bookTitle, fileName }: BookViewModalProps) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [mode, setMode] = useState<'pdf' | 'text' | null>(null)
  const [pdfUrl, setPdfUrl] = useState<string | null>(null)
  const [textPages, setTextPages] = useState<string[]>([])
  const [page, setPage] = useState(0)

  const isPdf = fileName?.toLowerCase().endsWith('.pdf')

  const loadFile = useCallback(async () => {
    if (!open || !bookId) return
    setLoading(true)
    setError('')
    setPdfUrl(null)
    setTextPages([])
    setPage(0)
    setMode(isPdf ? 'pdf' : 'text')
    try {
      const blob = await api.books.getFile(bookId)
      if (isPdf) {
        const url = URL.createObjectURL(blob)
        setPdfUrl(url)
      } else {
        const text = await blob.text()
        setTextPages(splitTextIntoPages(text))
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load file')
    } finally {
      setLoading(false)
    }
  }, [open, bookId, isPdf])

  useEffect(() => {
    if (open) loadFile()
  }, [open, loadFile])

  useEffect(() => {
    return () => {
      if (pdfUrl) URL.revokeObjectURL(pdfUrl)
    }
  }, [pdfUrl])

  if (!open) return null

  const totalPages = textPages.length
  const canPrev = page > 0
  const canNext = page < totalPages - 1

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50" aria-hidden onClick={onClose} />
      <div className="relative flex max-h-[90vh] w-full max-w-4xl flex-col rounded-xl border border-surface-border bg-surface shadow-xl">
        <div className="flex shrink-0 items-center justify-between border-b border-surface-border px-4 py-3">
          <h2 className="truncate text-lg font-semibold text-slate-900">{bookTitle}</h2>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-2 text-slate-500 transition hover:bg-surface-muted hover:text-slate-700"
            aria-label="Close"
          >
            <IconX className="h-5 w-5" />
          </button>
        </div>
        <div className="min-h-0 flex-1 overflow-auto p-4">
          {loading && (
            <div className="flex min-h-[300px] items-center justify-center">
              <span className="flex items-center gap-2 text-muted">
                <IconLoader2 className="h-6 w-6 animate-spin" />
                Loading...
              </span>
            </div>
          )}
          {error && (
            <div className="rounded-lg bg-red-50 px-4 py-3 text-error">{error}</div>
          )}
          {!loading && !error && isPdf && pdfUrl && (
            <iframe
              src={pdfUrl}
              title={bookTitle}
              className="h-[70vh] w-full rounded-lg border border-surface-border"
            />
          )}
          {!loading && !error && !isPdf && textPages.length > 0 && (
            <div className="space-y-4">
              <div className="rounded-lg border border-surface-border bg-surface-muted/30 p-4 font-mono text-sm leading-relaxed text-slate-800 whitespace-pre-wrap">
                {textPages[page]}
              </div>
              {totalPages > 1 && (
                <div className="flex items-center justify-between border-t border-surface-border pt-3">
                  <button
                    type="button"
                    onClick={() => setPage((p) => Math.max(0, p - 1))}
                    disabled={!canPrev}
                    className="btn-secondary inline-flex items-center gap-1 disabled:opacity-50 disabled:pointer-events-none"
                  >
                    <IconChevronLeft className="h-4 w-4" />
                    Previous
                  </button>
                  <span className="text-sm text-muted">
                    Page {page + 1} of {totalPages}
                  </span>
                  <button
                    type="button"
                    onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
                    disabled={!canNext}
                    className="btn-secondary inline-flex items-center gap-1 disabled:opacity-50 disabled:pointer-events-none"
                  >
                    Next
                    <IconChevronRight className="h-4 w-4" />
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
