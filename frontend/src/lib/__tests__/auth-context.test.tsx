import { render, screen, waitFor, act } from '@testing-library/react'
import { AuthProvider, useAuth } from '../auth-context'
import { api } from '../api'

jest.mock('../api', () => ({
  api: {
    auth: {
      me: jest.fn(),
      login: jest.fn(),
      signup: jest.fn(),
    },
  },
}))

// Test component that uses auth
function TestComponent() {
  const auth = useAuth()
  return (
    <div>
      {auth.loading ? (
        <div>Loading...</div>
      ) : auth.user ? (
        <div>User: {auth.user.email}</div>
      ) : (
        <div>Not logged in</div>
      )}
    </div>
  )
}

describe('AuthContext', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    localStorage.clear()
  })

  it('shows loading initially', () => {
    ;(api.auth.me as jest.Mock).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    )
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )
    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('shows not logged in when no token', async () => {
    ;(api.auth.me as jest.Mock).mockRejectedValue(new Error('Not authenticated'))
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )
    await waitFor(() => {
      expect(screen.getByText('Not logged in')).toBeInTheDocument()
    })
  })

  it('loads user when token exists', async () => {
    localStorage.setItem('token', 'test-token')
    ;(api.auth.me as jest.Mock).mockResolvedValue({
      id: 1,
      email: 'test@example.com',
      full_name: 'Test User',
    })

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )

    await waitFor(() => {
      expect(screen.getByText(/test@example.com/)).toBeInTheDocument()
    })
  })

  it('login sets token and refreshes user', async () => {
    ;(api.auth.login as jest.Mock).mockResolvedValue({ access_token: 'new-token' })
    ;(api.auth.me as jest.Mock).mockResolvedValue({
      id: 1,
      email: 'test@example.com',
      full_name: 'Test User',
    })

    function LoginTest() {
      const auth = useAuth()
      return (
        <div>
          <button onClick={() => auth.login('test@example.com', 'password')}>Login</button>
          {auth.user && <div>User: {auth.user.email}</div>}
        </div>
      )
    }

    render(
      <AuthProvider>
        <LoginTest />
      </AuthProvider>
    )

    const button = screen.getByText('Login')
    await act(async () => {
      button.click()
    })

    await waitFor(() => {
      expect(localStorage.getItem('token')).toBe('new-token')
      expect(screen.getByText(/test@example.com/)).toBeInTheDocument()
    })
  })

  it('logout clears user and token', async () => {
    localStorage.setItem('token', 'test-token')
    ;(api.auth.me as jest.Mock).mockResolvedValue({
      id: 1,
      email: 'test@example.com',
    })

    function LogoutTest() {
      const auth = useAuth()
      return (
        <div>
          <button onClick={() => auth.logout()}>Logout</button>
          {auth.user ? <div>User: {auth.user.email}</div> : <div>Not logged in</div>}
        </div>
      )
    }

    render(
      <AuthProvider>
        <LogoutTest />
      </AuthProvider>
    )

    await waitFor(() => {
      expect(screen.getByText(/test@example.com/)).toBeInTheDocument()
    })

    const button = screen.getByText('Logout')
    act(() => {
      button.click()
    })

    expect(localStorage.getItem('token')).toBeNull()
    expect(screen.getByText('Not logged in')).toBeInTheDocument()
  })

  it('throws error when useAuth used outside provider', () => {
    // Suppress console.error for this test
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {})

    expect(() => {
      render(<TestComponent />)
    }).toThrow('useAuth must be used inside AuthProvider')

    consoleSpy.mockRestore()
  })
})
