import { useState } from 'react'
import ClientRegister from './ClientRegister'
import Login from './Login'

function AuthGate({ onSuccess }) {
  const [mode, setMode] = useState('login')

  return (
    <>
      {mode === 'login' ? <Login onSuccess={onSuccess} /> : <ClientRegister onSuccess={onSuccess} />}

      <p className="auth-toggle">
        {mode === 'login' ? (
          <>
            ¿Sos cliente y no tenés cuenta?{' '}
            <button type="button" className="link-btn" onClick={() => setMode('register')}>
              Registrate
            </button>
          </>
        ) : (
          <>
            ¿Ya tenés cuenta?{' '}
            <button type="button" className="link-btn" onClick={() => setMode('login')}>
              Iniciá sesión
            </button>
          </>
        )}
      </p>
    </>
  )
}

export default AuthGate
