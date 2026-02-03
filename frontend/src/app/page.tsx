'use client'

import Link from 'next/link'
import { useAuth } from '@/lib/auth-context'
import { IconBook2, IconArrowRight, IconSparkles, IconUser, IconLoader2 } from '@tabler/icons-react'

export default function Home() {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="flex min-h-[70vh] flex-col items-center justify-center">
        <span className="flex items-center gap-2 text-muted">
          <IconLoader2 className="h-6 w-6 animate-spin" />
          Loading...
        </span>
      </div>
    )
  }

  if (user) {
    return (
      <div className="flex min-h-[70vh] flex-col items-center justify-center text-center">
        <div className="mb-8 flex h-16 w-16 items-center justify-center rounded-2xl bg-primary-100">
          <IconBook2 className="h-9 w-9 text-primary-600" />
        </div>
        <h1 className="page-title mb-3">Welcome back</h1>
        <p className="mb-10 max-w-md text-muted">
          Browse books, borrow and return, leave reviews, and get personalized recommendations.
        </p>
        <div className="flex flex-col gap-3 sm:flex-row sm:gap-4">
          <Link href="/books" className="btn-primary inline-flex items-center gap-2">
            Books
            <IconArrowRight className="h-4 w-4" />
          </Link>
          <Link href="/recommendations" className="btn-secondary inline-flex items-center gap-2">
            <IconSparkles className="h-4 w-4" />
            Recommendations
          </Link>
          <Link href="/profile" className="btn-secondary inline-flex items-center gap-2">
            <IconUser className="h-4 w-4" />
            Profile
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="flex min-h-[70vh] flex-col items-center justify-center text-center">
      <div className="mb-8 flex h-16 w-16 items-center justify-center rounded-2xl bg-primary-100">
        <IconBook2 className="h-9 w-9 text-primary-600" />
      </div>
      <h1 className="page-title mb-3">LuminaLib</h1>
      <p className="mb-10 max-w-md text-muted">
        Browse books, borrow and return, leave reviews, and get personalized recommendations.
      </p>
      <div className="flex flex-col gap-3 sm:flex-row sm:gap-4">
        <Link href="/signup" className="btn-primary inline-flex items-center gap-2">
          Get started
          <IconArrowRight className="h-4 w-4" />
        </Link>
        <Link href="/login" className="btn-secondary inline-flex items-center gap-2">
          Log in
        </Link>
      </div>
    </div>
  )
}
