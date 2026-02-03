import { render, screen } from '@testing-library/react'
import { Nav } from '../Nav'
import { AuthProvider } from '@/lib/auth-context'

function wrap(ui: React.ReactElement) {
  return <AuthProvider>{ui}</AuthProvider>
}

test('shows LuminaLib and login/signup when not logged in', async () => {
  render(wrap(<Nav />))
  expect(screen.getByText('LuminaLib')).toBeInTheDocument()
  const login = await screen.findByText('Log in')
  expect(login).toBeInTheDocument()
  expect(screen.getByText('Sign up')).toBeInTheDocument()
})
