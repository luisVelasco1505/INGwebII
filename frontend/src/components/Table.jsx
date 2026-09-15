function Table({ columns, rows, onEdit, onDelete, canEdit = true, canDelete, emptyLabel }) {
  const showActions = canEdit || canDelete

  if (rows.length === 0) {
    return <p className="table-empty">{emptyLabel || 'Sin registros todavía.'}</p>
  }

  return (
    <div className="table-wrap">
      <table className="table">
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col.key}>{col.label}</th>
            ))}
            {showActions && <th className="table-actions-col">Acciones</th>}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.id}>
              {columns.map((col) => (
                <td key={col.key}>{col.render ? col.render(row) : row[col.key]}</td>
              ))}
              {showActions && (
                <td className="table-actions">
                  {canEdit && (
                    <button type="button" className="table-btn" onClick={() => onEdit(row)}>
                      Editar
                    </button>
                  )}
                  {canDelete && (
                    <button
                      type="button"
                      className="table-btn table-btn--danger"
                      onClick={() => onDelete(row)}
                    >
                      Eliminar
                    </button>
                  )}
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default Table
