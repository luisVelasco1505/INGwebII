import { useEffect, useState } from 'react'
import { AuthError, createClient, deleteClient, listClients, updateClient } from '../api'
import Table from '../components/Table'

const EMPTY_FORM = { name: '', email: '', phone: '', address: '' }

const COLUMNS = [
  { key: 'name', label: 'Nombre' },
  { key: 'email', label: 'Email' },
  { key: 'phone', label: 'Teléfono' },
  { key: 'address', label: 'Dirección' },
]

function ClientsPage({ canDelete, onUnauthorized }) {
  const [clients, setClients] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [form, setForm] = useState(EMPTY_FORM)
  const [editingId, setEditingId] = useState(null)
  const [saving, setSaving] = useState(false)

  async function loadClients() {
    setLoading(true)
    setError('')
    try {
      const data = await listClients()
      setClients(data)
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

  function handleError(err) {
    if (err instanceof AuthError) {
      onUnauthorized()
      return
    }
    setError(err.message)
  }

  function startEdit(client) {
    setEditingId(client.id)
    setForm({
      name: client.name || '',
      email: client.email || '',
      phone: client.phone || '',
      address: client.address || '',
    })
  }

  function cancelEdit() {
    setEditingId(null)
    setForm(EMPTY_FORM)
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setSaving(true)
    try {
      if (editingId) {
        await updateClient(editingId, form)
      } else {
        await createClient(form)
      }
      cancelEdit()
      await loadClients()
    } catch (err) {
      handleError(err)
    } finally {
      setSaving(false)
    }
  }

  async function handleDelete(client) {
    if (!window.confirm(`¿Eliminar a ${client.name}? Esto borra también sus mascotas.`)) {
      return
    }
    setError('')
    try {
      await deleteClient(client.id)
      await loadClients()
    } catch (err) {
      handleError(err)
    }
  }

  return (
    <div className="crud-section">
      <form className="entity-form" onSubmit={handleSubmit}>
        <h3>{editingId ? 'Editar cliente' : 'Nuevo cliente'}</h3>
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
            <span>Email</span>
            <input
              type="email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
            />
          </label>
          <label className="field">
            <span>Teléfono</span>
            <input
              value={form.phone}
              onChange={(e) => setForm({ ...form, phone: e.target.value })}
            />
          </label>
          <label className="field">
            <span>Dirección</span>
            <input
              value={form.address}
              onChange={(e) => setForm({ ...form, address: e.target.value })}
            />
          </label>
        </div>

        {error && <p className="login-error">{error}</p>}

        <div className="form-actions">
          <button type="submit" className="login-submit" disabled={saving}>
            {editingId ? 'Guardar cambios' : 'Crear cliente'}
          </button>
          {editingId && (
            <button type="button" className="table-btn" onClick={cancelEdit}>
              Cancelar
            </button>
          )}
        </div>
      </form>

      {loading ? (
        <p>Cargando clientes...</p>
      ) : (
        <Table
          columns={COLUMNS}
          rows={clients}
          onEdit={startEdit}
          onDelete={handleDelete}
          canDelete={canDelete}
          emptyLabel="Todavía no hay clientes cargados."
        />
      )}
    </div>
  )
}

export default ClientsPage
