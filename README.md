# Sistema de Control Veterinario

Aplicación web para la gestión de una clínica veterinaria: clientes, mascotas, citas y autenticación de usuarios (admin, veterinario, cliente).

## Estructura del proyecto

```
.
├── backend/    Django + Django REST Framework (API)
├── frontend/   React + Vite (SPA)
└── docs/       Especificación OpenAPI de la API
```

## Backend (Django)

**Requisitos:** Python 3.11+

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # define DJANGO_SECRET_KEY y JWT_SECRET_KEY
python manage.py migrate
python manage.py create_admin --name "Admin" --email admin@example.com --password ****
python manage.py runserver
```

La API queda disponible en `http://127.0.0.1:8000/`. Endpoints principales:

| Método | Ruta                       | Descripción                     |
|--------|----------------------------|----------------------------------|
| GET    | `/health`                  | Estado del servicio              |
| POST   | `/auth/register`           | Registro de usuario              |
| POST   | `/auth/register-client`    | Registro de cliente              |
| POST   | `/auth/login`              | Inicio de sesión (JWT)           |
| GET/POST | `/clients`                | Listar / crear clientes          |
| GET/PUT/DELETE | `/clients/<id>`      | Detalle, actualizar, eliminar    |
| GET/POST | `/pets`                   | Listar / crear mascotas          |
| GET/PUT/DELETE | `/pets/<id>`         | Detalle, actualizar, eliminar    |
| GET/POST | `/appointments`           | Listar / crear citas             |
| GET/PUT/DELETE | `/appointments/<id>` | Detalle, actualizar, eliminar    |
| GET    | `/docs/`                    | Documentación Swagger UI         |

Especificación completa en [docs/openapi.yaml](docs/openapi.yaml).

### Tests

```bash
cd backend
python manage.py test
```

## Frontend (React + Vite)

**Requisitos:** Node.js 18+

```bash
cd frontend
npm install
cp .env.example .env    # define VITE_API_URL apuntando al backend
npm run dev
```

La aplicación queda disponible en `http://localhost:5173/`.

Otros scripts disponibles: `npm run build`, `npm run preview`, `npm run lint`.

## Documentación adicional

- [Documento_Sistema_Control_Veterinario_APA7.docx](Documento_Sistema_Control_Veterinario_APA7.docx) — documento del sistema en formato APA7.
