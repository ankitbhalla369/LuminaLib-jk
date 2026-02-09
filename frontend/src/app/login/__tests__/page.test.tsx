import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { useRouter } from 'next/navigation'
import toast from 'react-hot-toast'
import LoginPage from '../page'
import { useAuth } from '@/lib/auth-context'

jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}))

jest.mock('react-hot-toast', () => ({
  default: {
    success: jest.fn(),
    error: jest.fn(),
  },
}))

jest.mock('@/lib/auth-context', () => ({
  useAuth: jest.fn(),
}))

describe('LoginPage', () => {
  const mockPush = jest.fn()
  const mockLogin = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
    ;(useRouter as jest.Mock).mockReturnValue({ push: mockPush })
    ;(useAuth as jest.Mock).mockReturnValue({ login: mockLogin })
  })

  it('renders login form', () => {
    render(<LoginPage />)
    expect(screen.getByText('Log in')).toBeInTheDocument()
    expect(screen.getByLabelText('Email')).toBeInTheDocument()
    expect(screen.getByLabelText('Password')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /log in/i })).toBeInTheDocument()
  })

  it('shows signup link', () => {
    render(<LoginPage />)
    const signupLink = screen.getByText(/sign up/i)
    expect(signupLink).toBeInTheDocument()
    expect(signupLink.closest('a')).toHaveAttribute('href', '/signup')
  })

  it('handles form submission successfully', async () => {
    mockLogin.mockResolvedValue(undefined)
    render(<LoginPage />)

    const emailInput = screen.getByLabelText('Email')
    const passwordInput = screen.getByLabelText('Password')
    const submitButton = screen.getByRole('button', { name: /log in/i })

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } })
    fireEvent.change(passwordInput, { target: { value: 'password123' } })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'password123')
      expect(toast.success).toHaveBeenCalledWith('Logged in successfully')
      expect(mockPush).toHaveBeenCalledWith('/books')
    })
  })

  it('displays error on login failure', async () => {
    const errorMessage = 'Invalid credentials'
    mockLogin.mockRejectedValue(new Error(errorMessage))
    render(<LoginPage />)

    const emailInput = screen.getByLabelText('Email')
    const passwordInput = screen.getByLabelText('Password')
    const submitButton = screen.getByRole('button', { name: /log in/i })

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } })
    fireEvent.change(passwordInput, { target: { value: 'wrongpassword' } })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument()
      expect(toast.error).toHaveBeenCalledWith(errorMessage)
    })
  })

  it('validates required fields', () => {
    render(<LoginPage />)
    const emailInput = screen.getByLabelText('Email')
    const passwordInput = screen.getByLabelText('Password')

    expect(emailInput).toBeRequired()
    expect(passwordInput).toBeRequired()
  })
})
