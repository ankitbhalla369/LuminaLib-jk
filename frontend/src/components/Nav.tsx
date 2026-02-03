'use client'

import Link from 'next/link'
import { useAuth } from '@/lib/auth-context'
import { IconBook2, IconUser, IconLogout, IconLogin, IconUserPlus, IconSparkles, IconLoader2 } from '@tabler/icons-react'

export function Nav() {
  const { user, logout, loading } = useAuth()

  if (loading) {
    return (
      <header className="sticky top-0 z-10 border-b border-surface-border bg-surface shadow-sm">
        <div className="mx-auto flex h-14 max-w-4xl items-center justify-between px-4 sm:px-6">
          <Link href="/" className="flex items-center gap-2 font-semibold text-slate-900">
            <IconBook2 className="h-6 w-6 text-primary-600" />
            LuminaLib
          </Link>
          <span className="flex items-center gap-2 text-muted">
            <IconLoader2 className="h-4 w-4 animate-spin" />
            Loading...
          </span>
        </div>
      </header>
    )
  }

  return (
    <header className="sticky top-0 z-10 border-b border-surface-border bg-surface shadow-sm">
      <div className="mx-auto flex h-14 max-w-4xl items-center justify-between px-4 sm:px-6">
        <Link href="/" className="flex items-center gap-2 font-semibold text-slate-900 transition hover:text-primary-600">
          <IconBook2 className="h-6 w-6 text-primary-600" />
          LuminaLib
        </Link>
        <nav className="flex items-center gap-1 sm:gap-3">
          {user ? (
            <>
              <Link href="/books" className="flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-surface-muted hover:text-slate-900">
                <IconBook2 className="h-4 w-4" />
                <span className="hidden sm:inline">Books</span>
              </Link>
              <Link href="/recommendations" className="flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-surface-muted hover:text-slate-900">
                <IconSparkles className="h-4 w-4" />
                <span className="hidden sm:inline">Recommendations</span>
              </Link>
              <Link href="/profile" className="flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-surface-muted hover:text-slate-900">
                <IconUser className="h-4 w-4" />
                <span className="hidden sm:inline">Profile</span>
              </Link>
              <button onClick={logout} className="flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium text-slate-600 transition hover:bg-surface-muted hover:text-slate-900">
                <IconLogout className="h-4 w-4" />
                <span className="hidden sm:inline">Sign out</span>
              </button>
            </>
          ) : (
            <>
              <Link href="/login" className="flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-surface-muted hover:text-slate-900">
                <IconLogin className="h-4 w-4" />
                Log in
              </Link>
              <Link href="/signup" className="btn-primary flex items-center gap-1.5">
                <IconUserPlus className="h-4 w-4" />
                Sign up
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  )
}
