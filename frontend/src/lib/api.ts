const BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

function getToken(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem('token')
}

async function request<T>(
  path: string,
  opts: Omit<RequestInit, 'body'> & { body?: unknown } = {}
): Promise<T> {
  const { body, ...rest } = opts
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(rest.headers as Record<string, string>),
  }
  const token = getToken()
  if (token) headers['Authorization'] = `Bearer ${token}`
  const res = await fetch(`${BASE}${path}`, {
    ...rest,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || String(err) || res.statusText)
  }
  if (res.status === 204) return undefined as T
  return res.json()
}

async function formRequest<T>(path: string, form: FormData): Promise<T> {
  const token = getToken()
  const headers: Record<string, string> = {}
  if (token) headers['Authorization'] = `Bearer ${token}`
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers,
    body: form,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || String(err) || res.statusText)
  }
  return res.json()
}

export type User = { id: number; email: string; full_name: string | null; created_at: string }
export type Book = { id: number; title: string; author: string | null; genre: string | null; summary: string | null; created_at: string }
export type BookDetail = Book & {
  currently_borrowed_by_me: boolean
  can_review: boolean
  file_name?: string | null
  my_review?: { rating: number; text: string | null } | null
}
export type Review = { id: number; user_id: number; book_id: number; rating: number; text: string | null; created_at: string }

export const api = {
  auth: {
    signup: (email: string, password: string, full_name?: string) =>
      request<User>('/auth/signup', { method: 'POST', body: { email, password, full_name } }),
    login: (email: string, password: string) =>
      request<{ access_token: string }>('/auth/login', { method: 'POST', body: { email, password } }),
    me: () => request<User>('/auth/me'),
    updateMe: (full_name: string) =>
      request<User>('/auth/me', { method: 'PUT', body: { full_name } }),
  },
  books: {
    list: (skip = 0, limit = 20) =>
      request<{ items: Book[]; total: number; skip: number; limit: number }>(
        `/books?skip=${skip}&limit=${limit}`
      ),
    get: (id: number) => request<BookDetail>(`/books/${id}`),
    create: (form: FormData) => formRequest<Book>('/books', form),
    update: (id: number, data: { title?: string; author?: string; genre?: string }) =>
      request<Book>(`/books/${id}`, { method: 'PUT', body: data }),
    delete: (id: number) => request<unknown>(`/books/${id}`, { method: 'DELETE' }),
    borrow: (id: number) => request<unknown>(`/books/${id}/borrow`, { method: 'POST' }),
    return: (id: number) => request<unknown>(`/books/${id}/return`, { method: 'POST' }),
    review: (id: number, rating: number, text?: string) =>
      request<Review>(`/books/${id}/reviews`, { method: 'POST', body: { rating, text } }),
    analysis: (id: number) => request<{ summary: string | null; consensus: string | null }>(`/books/${id}/analysis`),
    getFile: async (id: number): Promise<Blob> => {
      const token = getToken()
      const res = await fetch(`${BASE}/books/${id}/file`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }))
        throw new Error((err as { detail?: string }).detail || res.statusText)
      }
      return res.blob()
    },
  },
  recommendations: {
    list: () => request<{ id: number; title: string; author: string | null; genre: string | null }[]>('/recommendations'),
    suggestions: (limit?: number) =>
      request<{ suggestions: { title: string; author: string; genre: string }[] }>(
        `/recommendations/suggestions${limit != null ? `?limit=${limit}` : ''}`
      ),
    suggestionsSimilar: (bookId: number, limit?: number) =>
      request<{ suggestions: { title: string; author: string; genre: string }[] }>(
        `/recommendations/suggestions/similar/${bookId}${limit != null ? `?limit=${limit}` : ''}`
      ),
    similar: (bookId: number, limit?: number) =>
      request<{ id: number; title: string; author: string | null; genre: string | null; score: number }[]>(
        `/recommendations/similar/${bookId}${limit != null ? `?limit=${limit}` : ''}`
      ),
  },
  preferences: {
    list: () => request<{ genre: string; weight: number }[]>('/preferences'),
    add: (genre: string, weight: number) =>
      request<unknown>('/preferences', { method: 'POST', body: { genre, weight } }),
  },
}
