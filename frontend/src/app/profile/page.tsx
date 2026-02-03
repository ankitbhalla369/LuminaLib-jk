'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import toast from 'react-hot-toast'
import { useAuth } from '@/lib/auth-context'
import { api } from '@/lib/api'
import { IconLoader2, IconUser } from '@tabler/icons-react'

export default function ProfilePage() {
  const { user, loading, refresh } = useAuth()
  const router = useRouter()
  const [fullName, setFullName] = useState('')
  const [err, setErr] = useState('')

  useEffect(() => {
    if (!loading && !user) router.push('/login')
    if (user) setFullName(user.full_name || '')
  }, [user, loading, router])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setErr('')
    try {
      await api.auth.updateMe(fullName)
      await refresh()
      toast.success('Profile updated')
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Update failed'
      setErr(msg)
      toast.error(msg)
    }
  }

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

  return (
    <div className="mx-auto max-w-md">
      <div className="card">
        <div className="mb-6 flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary-100">
            <IconUser className="h-6 w-6 text-primary-600" />
          </div>
          <h1 className="page-title">Profile</h1>
        </div>
        <form onSubmit={handleSubmit} className="space-y-5">
          {err && (
            <div className="rounded-lg bg-red-50 px-3 py-2 text-error">
              {err}
            </div>
          )}
          <div>
            <label className="label">Email</label>
            <p className="rounded-lg border border-surface-border bg-surface-muted px-3 py-2.5 text-slate-700">
              {user.email}
            </p>
          </div>
          <div>
            <label className="label">Full name</label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="input-field"
              placeholder="Your name"
            />
          </div>
          <button type="submit" className="btn-primary w-full">
            Save changes
          </button>
        </form>
      </div>
    </div>
  )
}
