import { useState } from 'react'
import { registerClient } from './api'
import { SPECIES } from './constants'

const EMPTY_FORM = {
  name: '',
  email: '',
  phone: '',
  address: '',
  password: '',
  petName: '',
  petSpecies: 'perro',
  petBreed: '',
  petAge: '',
  petWeight: '',
}

function ClientRegister({ onSuccess }) {
  const [form, setForm] = useState(EMPTY_FORM)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  function update(field) {
    return (e) => setForm({ ...form, [field]: e.target.value })
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setLoading(true)

    try {
      const data = await registerClient({
        name: form.name,
        email: form.email,
        phone: form.phone || null,
        address: form.address || null,
        password: form.password,
        pet: {
          name: form.petName,
          species: form.petSpecies,
          breed: form.petBreed || null,
          age: form.petAge === '' ? null : Number(form.petAge),
          weight: form.petWeight === '' ? null : Number(form.petWeight),
        },
      })
      onSuccess(data.user)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="card">
      <h2>Registrarme como cliente</h2>
      <form className="login-form" onSubmit={handleSubmit}>
        <div className="form-grid">
          <label className="field">
            <span>Tu nombre</span>
            <input value={form.name} onChange={update('name')} required />
          </label>
          <label className="field">
            <span>Email</span>
            <input type="email" value={form.email} onChange={update('email')} required />
          </label>
          <label className="field">
            <span>Teléfono</span>
            <input value={form.phone} onChange={update('phone')} />
          </label>
          <label className="field">
            <span>Dirección</span>
            <input value={form.address} onChange={update('address')} />
          </label>
          <label className="field">
            <span>Contraseña</span>
            <input
              type="password"
              value={form.password}
              onChange={update('password')}
              required
              autoComplete="new-password"
            />
          </label>
        </div>

        <h3 className="subform-title">Tu mascota</h3>
        <div className="form-grid">
          <label className="field">
            <span>Nombre</span>
            <input value={form.petName} onChange={update('petName')} required />
          </label>
          <label className="field">
            <span>Especie</span>
            <select value={form.petSpecies} onChange={update('petSpecies')}>
              {SPECIES.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </label>
          <label className="field">
            <span>Raza</span>
            <input value={form.petBreed} onChange={update('petBreed')} />
          </label>
          <label className="field">
            <span>Edad</span>
            <input type="number" min="0" value={form.petAge} onChange={update('petAge')} />
          </label>
          <label className="field">
            <span>Peso (kg)</span>
            <input
              type="number"
              min="0"
              step="0.1"
              value={form.petWeight}
              onChange={update('petWeight')}
            />
          </label>
        </div>

        {error && <p className="login-error">{error}</p>}

        <button type="submit" className="login-submit" disabled={loading}>
          {loading ? 'Creando cuenta...' : 'Crear mi cuenta'}
        </button>
      </form>
    </section>
  )
}

export default ClientRegister
