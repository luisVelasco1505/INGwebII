import { useEffect, useState } from 'react'
import { getHealth } from './api'
import './App.css'

function App() {
  const [status, setStatus] = useState('cargando...')
  const [error, setError] = useState(null)

  useEffect(() => {
    getHealth()
      .then((data) => setStatus(data.status))
      .catch((err) => setError(err.message))
  }, [])

  return (
    <section id="center">
      <h1>Sistema de Gestión de Proyectos y Tareas</h1>
      <p>
        Estado del backend:{' '}
        <strong>{error ? `error - ${error}` : status}</strong>
      </p>
    </section>
  )
}

export default App
