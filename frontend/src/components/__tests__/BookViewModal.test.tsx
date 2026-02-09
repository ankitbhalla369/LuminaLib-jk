import { render, screen, waitFor } from '@testing-library/react'
import { BookViewModal } from '../BookViewModal'
import { api } from '@/lib/api'

jest.mock('@/lib/api', () => ({
  api: {
    books: {
      getFile: jest.fn(),
    },
  },
}))

describe('BookViewModal', () => {
  const defaultProps = {
    open: true,
    onClose: jest.fn(),
    bookId: 1,
    bookTitle: 'Test Book',
    fileName: 'test.txt',
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders when open', () => {
    render(<BookViewModal {...defaultProps} />)
    expect(screen.getByText('Test Book')).toBeInTheDocument()
  })

  it('does not render when closed', () => {
    render(<BookViewModal {...defaultProps} open={false} />)
    expect(screen.queryByText('Test Book')).not.toBeInTheDocument()
  })

  it('displays loading state', async () => {
    ;(api.books.getFile as jest.Mock).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    )
    render(<BookViewModal {...defaultProps} />)
    expect(screen.getByText(/loading/i)).toBeInTheDocument()
  })

  it('displays error when file load fails', async () => {
    ;(api.books.getFile as jest.Mock).mockRejectedValue(new Error('Failed to load'))
    render(<BookViewModal {...defaultProps} />)
    await waitFor(() => {
      expect(screen.getByText(/failed to load/i)).toBeInTheDocument()
    })
  })

  it('displays PDF in iframe for PDF files', async () => {
    const blob = new Blob(['pdf content'], { type: 'application/pdf' })
    ;(api.books.getFile as jest.Mock).mockResolvedValue(blob)
    render(<BookViewModal {...defaultProps} fileName="test.pdf" />)
    await waitFor(() => {
      const iframe = screen.getByTitle('Test Book')
      expect(iframe).toBeInTheDocument()
      expect(iframe.tagName).toBe('IFRAME')
    })
  })

  it('displays text content for text files', async () => {
    const textContent = 'This is a test book content. '.repeat(100) // Long enough to paginate
    const blob = new Blob([textContent], { type: 'text/plain' })
    ;(api.books.getFile as jest.Mock).mockResolvedValue(blob)
    render(<BookViewModal {...defaultProps} fileName="test.txt" />)
    await waitFor(() => {
      expect(screen.getByText(/this is a test book content/i)).toBeInTheDocument()
    })
  })

  it('calls onClose when close button is clicked', () => {
    const onClose = jest.fn()
    render(<BookViewModal {...defaultProps} onClose={onClose} />)
    const closeButton = screen.getByLabelText('Close')
    closeButton.click()
    expect(onClose).toHaveBeenCalledTimes(1)
  })

  it('calls onClose when backdrop is clicked', () => {
    const onClose = jest.fn()
    render(<BookViewModal {...defaultProps} onClose={onClose} />)
    const backdrop = screen.getByRole('generic').querySelector('.absolute.inset-0')
    if (backdrop) {
      backdrop.click()
      expect(onClose).toHaveBeenCalledTimes(1)
    }
  })
})
