import { render, screen } from '@testing-library/react'
import { BookCard } from '../BookCard'

const book = {
  id: 1,
  title: 'Test Book',
  author: 'Test Author',
  genre: 'Fiction',
}

test('renders book title, author, and genre', () => {
  render(
    <ul>
      <BookCard book={book} />
    </ul>
  )
  expect(screen.getByText('Test Book')).toBeInTheDocument()
  expect(screen.getByText('Test Author')).toBeInTheDocument()
  expect(screen.getByText('Fiction')).toBeInTheDocument()
})

test('links to book detail by default', () => {
  render(
    <ul>
      <BookCard book={book} />
    </ul>
  )
  const link = screen.getByRole('link', { name: /test book/i })
  expect(link).toHaveAttribute('href', '/books/1')
})

test('uses custom href when provided', () => {
  render(
    <ul>
      <BookCard book={book} href="/custom/1" />
    </ul>
  )
  const link = screen.getByRole('link', { name: /test book/i })
  expect(link).toHaveAttribute('href', '/custom/1')
})

test('omits author when null', () => {
  render(
    <ul>
      <BookCard book={{ ...book, author: null }} />
    </ul>
  )
  expect(screen.getByText('Test Book')).toBeInTheDocument()
  expect(screen.queryByText('Test Author')).not.toBeInTheDocument()
})
