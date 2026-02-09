import { api } from '../api'

// Mock fetch globally
global.fetch = jest.fn()

describe('API Client', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    localStorage.clear()
  })

  describe('auth', () => {
    it('signup makes correct request', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: 1, email: 'test@example.com', full_name: 'Test User' }),
      })

      await api.auth.signup('test@example.com', 'password', 'Test User')

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/auth/signup'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
          body: JSON.stringify({
            email: 'test@example.com',
            password: 'password',
            full_name: 'Test User',
          }),
        })
      )
    })

    it('login makes correct request', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ access_token: 'token123' }),
      })

      await api.auth.login('test@example.com', 'password')

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/auth/login'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({
            email: 'test@example.com',
            password: 'password',
          }),
        })
      )
    })

    it('me includes auth token', async () => {
      localStorage.setItem('token', 'test-token')
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: 1, email: 'test@example.com' }),
      })

      await api.auth.me()

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/auth/me'),
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: 'Bearer test-token',
          }),
        })
      )
    })
  })

  describe('books', () => {
    it('list makes correct request', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ items: [], total: 0, skip: 0, limit: 20 }),
      })

      await api.books.list(0, 20)

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/books?skip=0&limit=20'),
        expect.any(Object)
      )
    })

    it('get makes correct request', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: 1, title: 'Test Book' }),
      })

      await api.books.get(1)

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/books/1'),
        expect.any(Object)
      )
    })

    it('create uses FormData', async () => {
      const formData = new FormData()
      formData.append('title', 'Test Book')
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: 1, title: 'Test Book' }),
      })

      await api.books.create(formData)

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/books'),
        expect.objectContaining({
          method: 'POST',
          body: formData,
        })
      )
    })

    it('getFile returns blob', async () => {
      const blob = new Blob(['content'], { type: 'text/plain' })
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        blob: async () => blob,
      })

      const result = await api.books.getFile(1)

      expect(result).toBeInstanceOf(Blob)
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/books/1/file'),
        expect.any(Object)
      )
    })
  })

  describe('error handling', () => {
    it('throws error on failed request', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        statusText: 'Not Found',
        json: async () => ({ detail: 'Book not found' }),
      })

      await expect(api.books.get(999)).rejects.toThrow('Book not found')
    })

    it('handles non-JSON error responses', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        statusText: 'Internal Server Error',
        json: async () => {
          throw new Error('Invalid JSON')
        },
      })

      await expect(api.books.get(1)).rejects.toThrow('Internal Server Error')
    })
  })
})
