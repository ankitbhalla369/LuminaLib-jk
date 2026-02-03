import { render, screen } from '@testing-library/react'
import { ErrorMessage } from '../ErrorMessage'

test('renders nothing when message is empty', () => {
  const { container } = render(<ErrorMessage message="" />)
  expect(container.firstChild).toBeNull()
})

test('renders error message with role alert', () => {
  render(<ErrorMessage message="Something went wrong" />)
  const alert = screen.getByRole('alert')
  expect(alert).toHaveTextContent('Something went wrong')
})

test('applies custom className', () => {
  render(<ErrorMessage message="Error" className="mt-4" />)
  const el = screen.getByRole('alert')
  expect(el).toHaveClass('mt-4')
})
