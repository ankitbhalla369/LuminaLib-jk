'use client'

import { useEffect } from 'react'
import { IconAlertCircle } from '@tabler/icons-react'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error(error)
  }, [error])

  return (
    <div className="flex min-h-[50vh] flex-col items-center justify-center px-4">
      <div className="card max-w-md w-full text-center">
        <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-xl bg-red-100">
          <IconAlertCircle className="h-8 w-8 text-red-600" />
        </div>
        <h2 className="page-title mb-2">Something went wrong</h2>
        <p className="text-muted mb-6">{error.message}</p>
        <button onClick={reset} className="btn-primary w-full sm:w-auto">
          Try again
        </button>
      </div>
    </div>
  )
}
