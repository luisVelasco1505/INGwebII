import { useEffect, useState } from 'react'
import { getHealth, getStoredUser, getToken, logout } from './api'
import Login from './Login'
import './App.css'

const SESSIONS = [
  { id: 1, title: 'Entorno y primer backend', detail: 'Flask + /health' },
  {
    id: 2,
    title: 'Modelo de datos y JWT',
    detail: 'Clientes, mascotas y citas + login con roles',
  },
  { id: 3, title: 'Frontend con React', detail: 'Vite + login contra el backend' },
]

const STACK = ['React', 'Vite', 'Flask', 'SQLAlchemy', 'JWT']

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

  return (
    <div id="page">
      <header id="hero">
        <p className="eyebrow">Ingeniería Web II</p>
        <h1>Sistema de Control Veterinario</h1>
        <p className="lead">
          Gestión de clientes, mascotas y citas para una clínica veterinaria.
          Backend en Flask con autenticación JWT, frontend en React.
        </p>
        <StatusBadge state={state} />
        {detail && <code className="detail">{detail}</code>}
      </header>

      {user ? (
        <section className="card">
          <h2>Sesión iniciada</h2>
          <p className="session-info">
            {user.name} · <span className="pill pill--role">{user.role}</span>
          </p>
          <button type="button" className="login-submit" onClick={handleLogout}>
            Cerrar sesión
          </button>
        </section>
      ) : (
        <Login onSuccess={setUser} />
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
