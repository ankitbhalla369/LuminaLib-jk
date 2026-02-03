'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import toast from 'react-hot-toast'
import { useAuth } from '@/lib/auth-context'
import { api } from '@/lib/api'
import { IconSparkles, IconChevronRight, IconLoader2, IconBook2 } from '@tabler/icons-react'

type Rec = { id: number; title: string; author: string | null; genre: string | null }

export default function RecommendationsPage() {
  const { user, loading } = useAuth()
  const router = useRouter()
  const [items, setItems] = useState<Rec[]>([])
  const [err, setErr] = useState('')
  const [prefGenre, setPrefGenre] = useState('')
  const [prefWeight, setPrefWeight] = useState(1)
  const [prefMsg, setPrefMsg] = useState('')
  const [genrePrefs, setGenrePrefs] = useState<{ genre: string; weight: number }[]>([])
  const [aiSuggestions, setAiSuggestions] = useState<{ title: string; author: string; genre: string }[]>([])
  const [loadingRecs, setLoadingRecs] = useState(true)

  useEffect(() => {
    if (!loading && !user) router.push('/login')
  }, [user, loading, router])

  function loadRecommendations() {
    if (!user) return
    setLoadingRecs(true)
    setErr('')
    Promise.all([
      api.recommendations.list().then(setItems).catch((e) => setErr(e instanceof Error ? e.message : 'Failed')),
      api.preferences.list().then(setGenrePrefs).catch(() => setGenrePrefs([])),
      api.recommendations.suggestions(10).then((r) => setAiSuggestions(r.suggestions || [])).catch(() => setAiSuggestions([])),
    ]).finally(() => setLoadingRecs(false))
  }

  useEffect(() => {
    if (!user) return
    loadRecommendations()
  }, [user])

  async function addPreference(e: React.FormEvent) {
    e.preventDefault()
    if (!prefGenre.trim()) return
    setPrefMsg('')
    try {
      await api.preferences.add(prefGenre.trim(), prefWeight)
      toast.success('Genre preference added')
      loadRecommendations()
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Failed'
      setPrefMsg(msg)
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
    <div className="space-y-6">
      <h1 className="page-title flex items-center gap-2">
        <IconSparkles className="h-8 w-8 text-primary-600" />
        Recommendations
      </h1>
      <p className="text-muted">Add a genre below to see two kinds of recommendations: books in your library (by genre) and AI suggestions for books not in the catalog.</p>
      <div className="card">
        <h2 className="font-semibold text-slate-900 mb-3">Genre preferences (used for AI recommendations)</h2>
        {genrePrefs.length > 0 && (
          <div className="mb-4 flex flex-wrap gap-2">
            {genrePrefs.map((p) => (
              <span
                key={p.genre}
                className="inline-flex items-center rounded-full bg-primary-100 px-3 py-1 text-sm font-medium text-primary-800"
              >
                {p.genre} (weight {p.weight})
              </span>
            ))}
          </div>
        )}
        <form onSubmit={addPreference} className="flex flex-wrap items-end gap-4">
          <div className="min-w-[140px] flex-1">
            <label className="label">Genre</label>
            <input
              type="text"
              value={prefGenre}
              onChange={(e) => setPrefGenre(e.target.value)}
              className="input-field"
              placeholder="e.g. Fiction, Sci-Fi"
            />
          </div>
          <div className="w-24">
            <label className="label">Weight</label>
            <input
              type="number"
              step="0.1"
              min="0.1"
              value={prefWeight}
              onChange={(e) => setPrefWeight(Number(e.target.value))}
              className="input-field"
            />
          </div>
          <button type="submit" className="btn-primary">
            Add
          </button>
        </form>
        {prefMsg && (
          <p className="mt-3 text-sm text-error">
            {prefMsg}
          </p>
        )}
      </div>
      {err && (
        <div className="rounded-lg bg-red-50 px-4 py-3 text-error">
          {err}
        </div>
      )}
      {loadingRecs && (
        <div className="card flex min-h-[200px] items-center justify-center py-12">
          <span className="flex items-center gap-2 text-muted">
            <IconLoader2 className="h-6 w-6 animate-spin" />
            Loading recommendations...
          </span>
        </div>
      )}
      {!loadingRecs && items.length === 0 && !err && (
        <div className="card text-center py-12">
          <IconBook2 className="mx-auto h-12 w-12 text-slate-300 mb-4" />
          <p className="text-muted mb-2">No recommendations yet.</p>
          <p className="text-sm text-muted">Add a genre above (e.g. Fiction, Sci-Fi). Books in the catalog that match your genre preferences will appear here.</p>
        </div>
      )}
      {!loadingRecs && aiSuggestions.length > 0 && (
        <div className="space-y-3">
          <h2 className="font-semibold text-slate-900 flex items-center gap-2">
            <IconSparkles className="h-5 w-5 text-primary-600" />
            You might also like (not in your library)
          </h2>
          <p className="text-sm text-muted">AI suggestions based on your genre preferences. These books are not in the catalog.</p>
          <ul className="grid gap-3 sm:grid-cols-2 lg:grid-cols-1">
            {aiSuggestions.map((s, i) => (
              <li key={`${s.title}-${i}`} className="card flex items-center gap-4">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary-100">
                  <IconBook2 className="h-5 w-5 text-primary-600" />
                </div>
                <div className="min-w-0 flex-1">
                  <h3 className="font-semibold text-slate-900 truncate">{s.title}</h3>
                  <p className="text-sm text-muted">{s.author}</p>
                  {s.genre && (
                    <span className="mt-1 inline-block rounded-full bg-primary-50 px-2 py-0.5 text-xs font-medium text-primary-700">
                      {s.genre}
                    </span>
                  )}
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
      {!loadingRecs && items.length > 0 && (
        <div className="space-y-3">
          <h2 className="font-semibold text-slate-900">
            In your library (by genre)
          </h2>
          <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-1">
            {items.map((b) => {
              const matchesGenre = genrePrefs.some(
                (p) => b.genre && p.genre.toLowerCase() === b.genre.toLowerCase()
              )
              return (
                <li key={b.id}>
                  <Link href={`/books/${b.id}`} className="card-hover flex items-center justify-between gap-4">
                    <div className="min-w-0 flex-1">
                      <h3 className="font-semibold text-slate-900 truncate">{b.title}</h3>
                      {b.author && <p className="text-sm text-muted mt-0.5">{b.author}</p>}
                      <div className="mt-2 flex flex-wrap items-center gap-2">
                        {b.genre && (
                          <span className="inline-block rounded-full bg-primary-50 px-2.5 py-0.5 text-xs font-medium text-primary-700">
                            {b.genre}
                          </span>
                        )}
                        {matchesGenre && (
                          <span className="text-xs text-primary-600">
                            Matches your interest
                          </span>
                        )}
                      </div>
                    </div>
                    <IconChevronRight className="h-5 w-5 shrink-0 text-slate-400" />
                  </Link>
                </li>
              )
            })}
          </ul>
        </div>
      )}
    </div>
  )
}
