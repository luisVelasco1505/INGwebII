import { useEffect, useState } from 'react'
import { getHealth, getStoredUser, getToken, logout } from './api'
import AuthGate from './AuthGate'
import AppointmentsPage from './pages/AppointmentsPage'
import ClientDashboard from './pages/ClientDashboard'
import ClientsPage from './pages/ClientsPage'
import PetsPage from './pages/PetsPage'
import './App.css'

const SESSIONS = [
  { id: 1, title: 'Entorno y primer backend', detail: 'Django REST Framework + /health' },
  {
    id: 2,
    title: 'Modelo de datos y JWT',
    detail: 'Clientes, mascotas y citas + login con roles',
  },
  {
    id: 3,
    title: 'Frontend con React',
    detail: 'Login y pantallas CRUD contra el backend',
  },
]

const STACK = ['React', 'Vite', 'Django', 'DRF', 'JWT']

const TABS = [
  { id: 'clients', label: 'Clientes' },
  { id: 'pets', label: 'Mascotas' },
  { id: 'appointments', label: 'Citas' },
]

function StatusBadge({ state }) {
  const label = {
    loading: 'Conectando...',
    ok: 'Backend conectado',
    error: 'Backend no disponible',
  }[state]

  return (
    <span className={`badge badge--${state}`}>
      <span className="badge__dot" />
      {label}
    </span>
  )
}

function App() {
  const [state, setState] = useState('loading')
  const [detail, setDetail] = useState('')
  const [user, setUser] = useState(() => (getToken() ? getStoredUser() : null))
  const [view, setView] = useState('clients')

  useEffect(() => {
    getHealth()
      .then((data) => {
        setState('ok')
        setDetail(JSON.stringify(data))
      })
      .catch((err) => {
        setState('error')
        setDetail(err.message)
      })
  }, [])

  function handleLogout() {
    logout()
    setUser(null)
  }

  const canDelete = user?.role === 'admin'
  const pageProps = { canDelete, onUnauthorized: handleLogout }

  return (
    <div id="page">
      <header id="hero">
        <p className="eyebrow">Ingeniería Web II</p>
        <h1>Sistema de Control Veterinario</h1>
        <p className="lead">
          Gestión de clientes, mascotas y citas para una clínica veterinaria.
          Backend en Django REST Framework con autenticación JWT, frontend en React.
        </p>
        <StatusBadge state={state} />
        {detail && <code className="detail">{detail}</code>}
      </header>

      {user ? (
        <section className="card card--wide">
          <div className="session-bar">
            <p className="session-info">
              {user.name} · <span className="pill pill--role">{user.role}</span>
            </p>
            <button type="button" className="login-submit" onClick={handleLogout}>
              Cerrar sesión
            </button>
          </div>

          {user.role === 'client' ? (
            <ClientDashboard onUnauthorized={handleLogout} />
          ) : (
            <>
              <nav className="tabs">
                {TABS.map((tab) => (
                  <button
                    key={tab.id}
                    type="button"
                    className={`tab ${view === tab.id ? 'tab--active' : ''}`}
                    onClick={() => setView(tab.id)}
                  >
                    {tab.label}
                  </button>
                ))}
              </nav>

              {view === 'clients' && <ClientsPage {...pageProps} />}
              {view === 'pets' && <PetsPage {...pageProps} />}
              {view === 'appointments' && <AppointmentsPage {...pageProps} />}
            </>
          )}
        </section>
      ) : (
        <AuthGate onSuccess={setUser} />
      )}

      <section className="card">
        <h2>Progreso del proyecto</h2>
        <ol className="sessions">
          {SESSIONS.map((s) => (
            <li key={s.id} className="session">
              <span className="session__check">✓</span>
              <div>
                <p className="session__title">
                  Sesión {s.id} — {s.title}
                </p>
                <p className="session__detail">{s.detail}</p>
              </div>
            </li>
          ))}
        </ol>
      </section>

      <footer id="stack">
        {STACK.map((tech) => (
          <span key={tech} className="pill">
            {tech}
          </span>
        ))}
      </footer>
    </div>
  )
}

export default App
