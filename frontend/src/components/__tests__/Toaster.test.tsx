import { render } from '@testing-library/react'
import { Toaster } from '../Toaster'

// Mock react-hot-toast
jest.mock('react-hot-toast', () => ({
  Toaster: jest.fn(() => <div data-testid="toaster">Toaster</div>),
}))

describe('Toaster', () => {
  it('renders the toast component', () => {
    const { getByTestId } = render(<Toaster />)
    expect(getByTestId('toaster')).toBeInTheDocument()
  })
})
