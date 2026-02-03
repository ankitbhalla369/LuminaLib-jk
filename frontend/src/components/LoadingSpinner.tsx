import { IconLoader2 } from '@tabler/icons-react'

interface LoadingSpinnerProps {
  message?: string
  className?: string
}

export function LoadingSpinner({ message = 'Loading...', className = '' }: LoadingSpinnerProps) {
  return (
    <div
      className={`flex min-h-[200px] items-center justify-center py-12 ${className}`}
      role="status"
      aria-label={message}
    >
      <span className="flex items-center gap-2 text-muted">
        <IconLoader2 className="h-5 w-5 animate-spin" aria-hidden />
        {message}
      </span>
    </div>
  )
}
