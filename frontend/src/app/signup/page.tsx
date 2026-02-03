'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import toast from 'react-hot-toast'
import { useAuth } from '@/lib/auth-context'

export default function SignupPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [err, setErr] = useState('')
  const { signup } = useAuth()
  const router = useRouter()

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setErr('')
    try {
      await signup(email, password, fullName || undefined)
      toast.success('Account created successfully')
      router.push('/books')
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Signup failed'
      setErr(msg)
      toast.error(msg)
    }
  }

  return (
    <div className="mx-auto w-full max-w-md">
      <div className="card">
        <h1 className="page-title mb-6">Sign up</h1>
        <form onSubmit={handleSubmit} className="space-y-5">
          {err && <p className="text-error rounded-lg bg-red-50 px-3 py-2">{err}</p>}
          <div>
            <label className="label">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="input-field"
              placeholder="you@example.com"
              required
            />
          </div>
          <div>
            <label className="label">Full name</label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="input-field"
              placeholder="Optional"
            />
          </div>
          <div>
            <label className="label">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input-field"
              required
            />
          </div>
          <button type="submit" className="btn-primary w-full">
            Sign up
          </button>
        </form>
        <p className="mt-6 text-center text-sm text-muted">
          Already have an account?{' '}
          <Link href="/login" className="font-medium text-primary-600 hover:text-primary-700">
            Log in
          </Link>
        </p>
      </div>
    </div>
  )
}
