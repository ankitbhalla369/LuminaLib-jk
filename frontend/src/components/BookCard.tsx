import Link from 'next/link'
import { IconChevronRight } from '@tabler/icons-react'
import type { Book } from '@/lib/api'

interface BookCardProps {
  book: Pick<Book, 'id' | 'title' | 'author' | 'genre'>
  href?: string
  className?: string
}

export function BookCard({ book, href, className = '' }: BookCardProps) {
  const to = href ?? `/books/${book.id}`
  return (
    <li className={className}>
      <Link href={to} className="card-hover flex items-center justify-between gap-4">
        <div className="min-w-0 flex-1">
          <h2 className="font-semibold text-slate-900 truncate">{book.title}</h2>
          {book.author && <p className="text-sm text-muted mt-0.5">{book.author}</p>}
          {book.genre && (
            <span className="mt-2 inline-block rounded-full bg-primary-50 px-2.5 py-0.5 text-xs font-medium text-primary-700">
              {book.genre}
            </span>
          )}
        </div>
        <IconChevronRight className="h-5 w-5 shrink-0 text-slate-400" aria-hidden />
      </Link>
    </li>
  )
}
