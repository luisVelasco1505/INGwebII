import { useEffect, useState } from 'react'
import {
  AuthError,
  createAppointment,
  deleteAppointment,
  listAppointments,
  listPets,
  updateAppointment,
} from '../api'
import Table from '../components/Table'
import { APPOINTMENT_STATUSES as STATUSES } from '../constants'

const EMPTY_FORM = {
  pet_id: '',
  date: '',
  reason: '',
  diagnosis: '',
  treatment: '',
  status: 'pendiente',
}

function AppointmentsPage({ canDelete, onUnauthorized }) {
  const [appointments, setAppointments] = useState([])
  const [pets, setPets] = useState([])
  const [petFilter, setPetFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [form, setForm] = useState(EMPTY_FORM)
  const [editingId, setEditingId] = useState(null)
  const [saving, setSaving] = useState(false)

  function handleError(err) {
    if (err instanceof AuthError) {
      onUnauthorized()
      return
    }
    setError(err.message)
  }

  async function loadPets() {
    try {
      setPets(await listPets())
    } catch (err) {
      handleError(err)
    }
  }

  async function loadAppointments() {
    setLoading(true)
    setError('')
    try {
      const params = {}
      if (petFilter) params.pet_id = petFilter
      if (statusFilter) params.status = statusFilter
      setAppointments(await listAppointments(params))
    } catch (err) {
      handleError(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadPets()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    loadAppointments()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [petFilter, statusFilter])

  const petName = (petId) => pets.find((p) => p.id === petId)?.name || `#${petId}`

  const columns = [
    { key: 'pet_id', label: 'Mascota', render: (row) => petName(row.pet_id) },
    { key: 'date', label: 'Fecha', render: (row) => new Date(row.date).toLocaleString() },
    { key: 'reason', label: 'Motivo' },
    { key: 'diagnosis', label: 'Diagnóstico' },
    { key: 'treatment', label: 'Tratamiento' },
    { key: 'status', label: 'Estado' },
  ]

  function toDatetimeLocal(isoDate) {
    if (!isoDate) return ''
    const date = new Date(isoDate)
    const offset = date.getTimezoneOffset()
    const local = new Date(date.getTime() - offset * 60000)
    return local.toISOString().slice(0, 16)
  }

  function startEdit(appointment) {
    setEditingId(appointment.id)
    setForm({
      pet_id: appointment.pet_id,
      date: toDatetimeLocal(appointment.date),
      reason: appointment.reason || '',
      diagnosis: appointment.diagnosis || '',
      treatment: appointment.treatment || '',
      status: appointment.status || 'pendiente',
    })
  }

  function cancelEdit() {
    setEditingId(null)
    setForm(EMPTY_FORM)
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')

    if (!form.pet_id) {
      setError('Elegí la mascota para la cita')
      return
    }

    setSaving(true)
    try {
      const payload = {
        pet_id: Number(form.pet_id),
        date: form.date,
        reason: form.reason,
        diagnosis: form.diagnosis || null,
        treatment: form.treatment || null,
        status: form.status,
      }
      if (editingId) {
        await updateAppointment(editingId, payload)
      } else {
        await createAppointment(payload)
      }
      cancelEdit()
      await loadAppointments()
    } catch (err) {
      handleError(err)
    } finally {
      setSaving(false)
    }
  }

  async function handleDelete(appointment) {
    if (!window.confirm('¿Eliminar esta cita?')) {
      return
    }
    setError('')
    try {
      await deleteAppointment(appointment.id)
      await loadAppointments()
    } catch (err) {
      handleError(err)
    }
  }

  return (
    <div className="crud-section">
      <form className="entity-form" onSubmit={handleSubmit}>
        <h3>{editingId ? 'Editar cita' : 'Nueva cita'}</h3>
        <div className="form-grid">
          <label className="field">
            <span>Mascota</span>
            <select
              value={form.pet_id}
              onChange={(e) => setForm({ ...form, pet_id: e.target.value })}
              required
            >
              <option value="">Elegí una mascota</option>
              {pets.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
          </label>
          <label className="field">
            <span>Fecha y hora</span>
            <input
              type="datetime-local"
              value={form.date}
              onChange={(e) => setForm({ ...form, date: e.target.value })}
              required
            />
          </label>
          <label className="field">
            <span>Motivo</span>
            <input
              value={form.reason}
              onChange={(e) => setForm({ ...form, reason: e.target.value })}
              required
            />
          </label>
          <label className="field">
            <span>Estado</span>
            <select
              value={form.status}
              onChange={(e) => setForm({ ...form, status: e.target.value })}
            >
              {STATUSES.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </label>
          <label className="field field--wide">
            <span>Diagnóstico</span>
            <input
              value={form.diagnosis}
              onChange={(e) => setForm({ ...form, diagnosis: e.target.value })}
            />
          </label>
          <label className="field field--wide">
            <span>Tratamiento</span>
            <input
              value={form.treatment}
              onChange={(e) => setForm({ ...form, treatment: e.target.value })}
            />
          </label>
        </div>

        {error && <p className="login-error">{error}</p>}

        <div className="form-actions">
          <button type="submit" className="login-submit" disabled={saving}>
            {editingId ? 'Guardar cambios' : 'Crear cita'}
          </button>
          {editingId && (
            <button type="button" className="table-btn" onClick={cancelEdit}>
              Cancelar
            </button>
          )}
        </div>
      </form>

      <div className="filters-row">
        <label className="field filter-field">
          <span>Filtrar por mascota</span>
          <select value={petFilter} onChange={(e) => setPetFilter(e.target.value)}>
            <option value="">Todas las mascotas</option>
            {pets.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
        </label>
        <label className="field filter-field">
          <span>Filtrar por estado</span>
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="">Todos los estados</option>
            {STATUSES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </label>
      </div>

      {loading ? (
        <p>Cargando citas...</p>
      ) : (
        <Table
          columns={columns}
          rows={appointments}
          onEdit={startEdit}
          onDelete={handleDelete}
          canDelete={canDelete}
          emptyLabel="Todavía no hay citas cargadas."
        />
      )}
    </div>
  )
}

export default AppointmentsPage
