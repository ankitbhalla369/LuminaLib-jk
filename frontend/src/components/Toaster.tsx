'use client'

import { Toaster as HotToaster } from 'react-hot-toast'

export function Toaster() {
  return (
    <HotToaster
      position="top-center"
      toastOptions={{
        duration: 4000,
        className: '!rounded-lg !shadow-md',
        success: { iconTheme: { primary: 'var(--color-primary-600, #2563eb)', secondary: '#fff' } },
        error: { iconTheme: { primary: 'var(--color-error, #dc2626)', secondary: '#fff' } },
      }}
    />
  )
}
