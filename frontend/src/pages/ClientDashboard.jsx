import { useEffect, useState } from 'react'
import { AuthError, listAppointments, listClients, listPets } from '../api'
import Table from '../components/Table'

const PET_COLUMNS = [
  { key: 'name', label: 'Nombre' },
  { key: 'species', label: 'Especie' },
  { key: 'breed', label: 'Raza' },
  { key: 'age', label: 'Edad' },
  { key: 'weight', label: 'Peso (kg)' },
]

function ClientDashboard({ onUnauthorized }) {
  const [profile, setProfile] = useState(null)
  const [pets, setPets] = useState([])
  const [appointments, setAppointments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    async function load() {
      setLoading(true)
      setError('')
      try {
        const [clients, myPets, myAppointments] = await Promise.all([
          listClients(),
          listPets(),
          listAppointments(),
        ])
        setProfile(clients[0] || null)
        setPets(myPets)
        setAppointments(myAppointments)
      } catch (err) {
        if (err instanceof AuthError) {
          onUnauthorized()
          return
        }
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const petName = (petId) => pets.find((p) => p.id === petId)?.name || `#${petId}`

  const appointmentColumns = [
    { key: 'pet_id', label: 'Mascota', render: (row) => petName(row.pet_id) },
    { key: 'date', label: 'Fecha', render: (row) => new Date(row.date).toLocaleString() },
    { key: 'reason', label: 'Motivo' },
    { key: 'diagnosis', label: 'Diagnóstico' },
    { key: 'treatment', label: 'Tratamiento' },
    { key: 'status', label: 'Estado' },
  ]

  if (loading) {
    return <p>Cargando tu información...</p>
  }

  if (error) {
    return <p className="login-error">{error}</p>
  }

  return (
    <div className="crud-section">
      {profile && (
        <div>
          <h3>Mis datos</h3>
          <p className="profile-line">
            {profile.name} · {profile.email || 'sin email'} · {profile.phone || 'sin teléfono'}
            {profile.address ? ` · ${profile.address}` : ''}
          </p>
        </div>
      )}

      <div>
        <h3>Mis mascotas</h3>
        <Table
          columns={PET_COLUMNS}
          rows={pets}
          canEdit={false}
          canDelete={false}
          emptyLabel="Todavía no tenés mascotas cargadas."
        />
      </div>

      <div>
        <h3>Historial de citas</h3>
        <Table
          columns={appointmentColumns}
          rows={appointments}
          canEdit={false}
          canDelete={false}
          emptyLabel="Todavía no hay citas registradas."
        />
      </div>
    </div>
  )
}

export default ClientDashboard
