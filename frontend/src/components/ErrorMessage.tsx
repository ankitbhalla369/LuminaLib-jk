interface ErrorMessageProps {
  message: string
  className?: string
}

export function ErrorMessage({ message, className = '' }: ErrorMessageProps) {
  if (!message) return null
  return (
    <div
      className={`rounded-lg bg-red-50 px-4 py-3 text-error ${className}`}
      role="alert"
    >
      {message}
    </div>
  )
}
