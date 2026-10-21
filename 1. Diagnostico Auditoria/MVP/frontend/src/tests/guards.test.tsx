import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { describe, expect, it } from 'vitest'
import { AuthProvider } from '../auth/AuthProvider'
import { ProtectedRoute, PublicOnlyRoute } from '../auth/guards'
import { storeToken } from '../auth/tokenStorage'
import { createTestToken } from './helpers'

function renderRoutes(initialPath: string) {
  return render(
    <MemoryRouter initialEntries={[initialPath]}>
      <AuthProvider>
        <Routes>
          <Route element={<PublicOnlyRoute />}>
            <Route path="/login" element={<div>Página de login</div>} />
          </Route>
          <Route element={<ProtectedRoute />}>
            <Route path="/private" element={<div>Zona privada</div>} />
          </Route>
          <Route element={<ProtectedRoute allowedRoles={['admin']} />}>
            <Route path="/admin" element={<div>Zona admin</div>} />
          </Route>
          <Route path="/forbidden" element={<div>Acceso denegado</div>} />
        </Routes>
      </AuthProvider>
    </MemoryRouter>,
  )
}

describe('route guards', () => {
  it('redirige al login sin sesión', async () => {
    renderRoutes('/private')
    expect(await screen.findByText('Página de login')).toBeInTheDocument()
  })

  it('permite el acceso a una ruta protegida con sesión', async () => {
    storeToken(createTestToken('cliente'))
    renderRoutes('/private')
    expect(await screen.findByText('Zona privada')).toBeInTheDocument()
  })

  it('redirige a forbidden cuando el rol no está autorizado', async () => {
    storeToken(createTestToken('cliente'))
    renderRoutes('/admin')
    expect(await screen.findByText('Acceso denegado')).toBeInTheDocument()
  })

  it('permite el acceso al rol autorizado', async () => {
    storeToken(createTestToken('admin'))
    renderRoutes('/admin')
    expect(await screen.findByText('Zona admin')).toBeInTheDocument()
  })

  it('redirige al panel si ya hay sesión en una ruta pública', async () => {
    storeToken(createTestToken('cliente'))
    render(
      <MemoryRouter initialEntries={['/login']}>
        <AuthProvider>
          <Routes>
            <Route element={<PublicOnlyRoute />}>
              <Route path="/login" element={<div>Página de login</div>} />
            </Route>
            <Route element={<ProtectedRoute />}>
              <Route path="/" element={<div>Panel privado</div>} />
            </Route>
          </Routes>
        </AuthProvider>
      </MemoryRouter>,
    )
    expect(await screen.findByText('Panel privado')).toBeInTheDocument()
  })
})
