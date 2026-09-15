import { useEffect, useState } from 'react'
import {
  AuthError,
  createPet,
  deletePet,
  listClients,
  listPets,
  updatePet,
} from '../api'
import Table from '../components/Table'
import { SPECIES } from '../constants'

const EMPTY_FORM = { name: '', species: 'perro', breed: '', age: '', weight: '', client_id: '' }

function PetsPage({ canDelete, onUnauthorized }) {
  const [pets, setPets] = useState([])
  const [clients, setClients] = useState([])
  const [clientFilter, setClientFilter] = useState('')
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

  async function loadClients() {
    try {
      setClients(await listClients())
    } catch (err) {
      handleError(err)
    }
  }

  async function loadPets() {
    setLoading(true)
    setError('')
    try {
      const data = await listPets(clientFilter ? { client_id: clientFilter } : {})
      setPets(data)
    } catch (err) {
      handleError(err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadClients()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    loadPets()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [clientFilter])

  const clientName = (clientId) =>
    clients.find((c) => c.id === clientId)?.name || `#${clientId}`

  const columns = [
    { key: 'name', label: 'Nombre' },
    { key: 'species', label: 'Especie' },
    { key: 'breed', label: 'Raza' },
    { key: 'age', label: 'Edad' },
    { key: 'weight', label: 'Peso (kg)' },
    { key: 'client_id', label: 'Dueño', render: (row) => clientName(row.client_id) },
  ]

  function startEdit(pet) {
    setEditingId(pet.id)
    setForm({
      name: pet.name || '',
      species: pet.species || 'perro',
      breed: pet.breed || '',
      age: pet.age ?? '',
      weight: pet.weight ?? '',
      client_id: pet.client_id,
    })
  }

  function cancelEdit() {
    setEditingId(null)
    setForm(EMPTY_FORM)
  }

  function buildPayload() {
    return {
      name: form.name,
      species: form.species,
      breed: form.breed || null,
      age: form.age === '' ? null : Number(form.age),
      weight: form.weight === '' ? null : Number(form.weight),
      client_id: Number(form.client_id),
    }
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')

    if (!form.client_id) {
      setError('Elegí un cliente dueño de la mascota')
      return
    }

    setSaving(true)
    try {
      const payload = buildPayload()
      if (editingId) {
        await updatePet(editingId, payload)
      } else {
        await createPet(payload)
      }
      cancelEdit()
      await loadPets()
    } catch (err) {
      handleError(err)
    } finally {
      setSaving(false)
    }
  }

  async function handleDelete(pet) {
    if (!window.confirm(`¿Eliminar a ${pet.name}? Esto borra también sus citas.`)) {
      return
    }
    setError('')
    try {
      await deletePet(pet.id)
      await loadPets()
    } catch (err) {
      handleError(err)
    }
  }

  return (
    <div className="crud-section">
      <form className="entity-form" onSubmit={handleSubmit}>
        <h3>{editingId ? 'Editar mascota' : 'Nueva mascota'}</h3>
        <div className="form-grid">
          <label className="field">
            <span>Nombre</span>
            <input
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              required
            />
          </label>
          <label className="field">
            <span>Especie</span>
            <select
              value={form.species}
              onChange={(e) => setForm({ ...form, species: e.target.value })}
            >
              {SPECIES.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </label>
          <label className="field">
            <span>Raza</span>
            <input
              value={form.breed}
              onChange={(e) => setForm({ ...form, breed: e.target.value })}
            />
          </label>
          <label className="field">
            <span>Edad</span>
            <input
              type="number"
              min="0"
              value={form.age}
              onChange={(e) => setForm({ ...form, age: e.target.value })}
            />
          </label>
          <label className="field">
            <span>Peso (kg)</span>
            <input
              type="number"
              min="0"
              step="0.1"
              value={form.weight}
              onChange={(e) => setForm({ ...form, weight: e.target.value })}
            />
          </label>
          <label className="field">
            <span>Dueño</span>
            <select
              value={form.client_id}
              onChange={(e) => setForm({ ...form, client_id: e.target.value })}
              required
            >
              <option value="">Elegí un cliente</option>
              {clients.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </label>
        </div>

        {error && <p className="login-error">{error}</p>}

        <div className="form-actions">
          <button type="submit" className="login-submit" disabled={saving}>
            {editingId ? 'Guardar cambios' : 'Crear mascota'}
          </button>
          {editingId && (
            <button type="button" className="table-btn" onClick={cancelEdit}>
              Cancelar
            </button>
          )}
        </div>
      </form>

      <label className="field filter-field">
        <span>Filtrar por dueño</span>
        <select value={clientFilter} onChange={(e) => setClientFilter(e.target.value)}>
          <option value="">Todos los clientes</option>
          {clients.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
      </label>

      {loading ? (
        <p>Cargando mascotas...</p>
      ) : (
        <Table
          columns={columns}
          rows={pets}
          onEdit={startEdit}
          onDelete={handleDelete}
          canDelete={canDelete}
          emptyLabel="Todavía no hay mascotas cargadas."
        />
      )}
    </div>
  )
}

export default PetsPage
