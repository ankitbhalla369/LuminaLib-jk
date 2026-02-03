import { render, screen } from '@testing-library/react'
import { LoadingSpinner } from '../LoadingSpinner'

test('renders default loading message', () => {
  render(<LoadingSpinner />)
  expect(screen.getByRole('status', { name: 'Loading...' })).toBeInTheDocument()
  expect(screen.getByText('Loading...')).toBeInTheDocument()
})

test('renders custom message', () => {
  render(<LoadingSpinner message="Fetching books..." />)
  expect(screen.getByRole('status', { name: 'Fetching books...' })).toBeInTheDocument()
  expect(screen.getByText('Fetching books...')).toBeInTheDocument()
})

test('applies custom className', () => {
  const { container } = render(<LoadingSpinner className="min-h-[40vh]" />)
  const wrapper = container.firstChild as HTMLElement
  expect(wrapper).toHaveClass('min-h-[40vh]')
})
