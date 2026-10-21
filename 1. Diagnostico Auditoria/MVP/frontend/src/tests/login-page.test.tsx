import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { describe, expect, it } from 'vitest'
import { AuthProvider } from '../auth/AuthProvider'
import { LoginPage } from '../pages/auth/LoginPage'
import { createTestToken } from './helpers'
import { server } from './server'

const api = 'http://localhost:8000/api/v1'

function renderLogin() {
  return render(
    <MemoryRouter initialEntries={['/login']}>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<div>Panel autenticado</div>} />
        </Routes>
      </AuthProvider>
    </MemoryRouter>,
  )
}

describe('LoginPage', () => {
  it('inicia sesión y navega al panel', async () => {
    server.use(
      http.post(`${api}/auth/token`, () =>
        HttpResponse.json({
          access_token: createTestToken('cliente'),
          token_type: 'bearer',
        }),
      ),
    )
    const user = userEvent.setup()
    renderLogin()

    await user.type(screen.getByLabelText(/usuario/i), 'cliente')
    await user.type(screen.getByLabelText(/contraseña/i), 'ClientPass123!')
    await user.click(screen.getByRole('button', { name: 'Entrar' }))

    expect(await screen.findByText('Panel autenticado')).toBeInTheDocument()
  })

  it('muestra un mensaje claro con credenciales inválidas', async () => {
    server.use(
      http.post(`${api}/auth/token`, () =>
        HttpResponse.json(
          { detail: 'Credenciales de autenticación inválidas.' },
          { status: 401 },
        ),
      ),
    )
    const user = userEvent.setup()
    renderLogin()

    await user.type(screen.getByLabelText(/usuario/i), 'cliente')
    await user.type(screen.getByLabelText(/contraseña/i), 'incorrecta')
    await user.click(screen.getByRole('button', { name: 'Entrar' }))

    expect(
      await screen.findByText('Usuario o contraseña incorrectos.'),
    ).toBeInTheDocument()
  })
})
