# API de reservas de coworking

Backend para administrar espacios, empresas, horarios de disponibilidad y reservas de un coworking. Incluye autenticación y permisos de acceso para el personal interno.

## Tecnologías

- Python 3.14, FastAPI y Pydantic.
- PostgreSQL 16, SQLAlchemy y psycopg2.
- Alembic para migraciones.
- Docker Compose, uv, pytest y GitHub Actions.

## Instalación y ejecución


Requisitos: Docker con Compose v2 y uv.

```sh
uv sync --frozen
cp -n .env.example .env
uv run python -c 'import secrets; print(secrets.token_urlsafe(48))'
```

El secreto generado se guarda en `JWT_SECRET` dentro de `.env` (mínimo 32 bytes). `COOKIE_SECURE=false` en desarrollo HTTP y `true` en HTTPS. El archivo `.env` no se versiona.

```sh
docker compose up --build -d --wait
```

El inicio de la API aplica las migraciones y carga los datos de ejemplo.

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs

```sh
docker compose logs api  # Registros de la API
docker compose down      # Detener los servicios
```

Los datos se guardan en el volumen `postgres_data`. El comando `docker compose down -v` elimina los datos del entorno.

### pgAdmin (opcional)

```sh
docker compose up -d pgadmin
```

Disponible en http://localhost:8080. Las credenciales de pgAdmin y PostgreSQL se definen en `.env`. La conexión a PostgreSQL utiliza el host `db` y el puerto `5432`.

### Ejecución local de la API

Con `.env` configurado y PostgreSQL en ejecución:

```sh
docker compose up -d db
uv run --frozen alembic upgrade head
uv run --frozen python -m infrastructure.seeders
uv run --frozen uvicorn app.main:app --reload
```

La conexión se configura mediante `DB_*` o `DATABASE_URL`, que tiene prioridad.

## Autenticación

Registro, login, logout, JWT, rotación del refresh token y recuperación de contraseña mediante un enlace en JSON.

- **Lector:** acceso a las consultas GET de negocio.
- **Administrador:** acceso a las consultas y operaciones de escritura.

Las cuentas nuevas tienen el rol de lector. No existen cuentas administrativas predeterminadas.

```sh
docker compose exec api python -m scripts.set_role persona@example.com admin
```

El cambio de rol invalida las sesiones anteriores. El acceso a la API requiere un token Bearer; Swagger aplica el token tras el login.

## Endpoints

19 operaciones de negocio y 7 de autenticación, documentadas en Swagger.

| Método | Ruta | Estado exitoso |
|---|---|---|
| GET | `/espacios`, `/empresas`, `/disponibilidades`, `/reservas` | 200 |
| GET | `/{recurso}/{id}` | 200 |
| POST | `/espacios`, `/empresas`, `/disponibilidades`, `/reservas` | 201 |
| PUT | `/espacios/{id}`, `/empresas/{id}`, `/disponibilidades/{id}` | 200 |
| DELETE | `/espacios/{id}`, `/empresas/{id}`, `/disponibilidades/{id}` | 204 |
| POST | `/reservas/{id}/cancelar` | 200 |

Las colecciones admiten filtros y paginación. Ejemplo:

```text
GET /espacios?tipo=oficina&estado=activo&ordenar_por=capacidad&direccion=desc&pagina=1&limite=2
```

## Reglas de negocio

- Las reservas duran al menos 30 minutos.
- Solo las empresas y espacios activos pueden participar en reservas.
- Las reservas deben respetar los horarios de disponibilidad y no superar el mismo día UTC.
- No se permiten reservas activas superpuestas para un espacio o empresa.
- No se pueden cancelar reservas iniciadas o ya canceladas.
- El RUT de cada empresa es único y válido.
- No se eliminan espacios o empresas con registros relacionados.

## Estructura del proyecto

| Directorio | Contenido |
|---|---|
| `app/` | Configuración de FastAPI. |
| `domain/` | Entidades y reglas de negocio. |
| `application/` | Servicios y casos de uso. |
| `infrastructure/` | Modelos ORM, repositorios, mappers y seeders. |
| `presentation/` | Routers, DTOs y dependencias. |
| `migrations/` | Migraciones de Alembic. |
| `tests_manual/` | Comprobaciones y reportes históricos. |
| `docs/` | Documentación del proyecto. |

## Pruebas

```sh
make install
make test-unit
make test-integration
make test-e2e
make test
make test-down
```

Las pruebas utilizan bases de datos aisladas y exigen una cobertura mínima del 85 %. Los reportes se generan en `reports/`, incluyendo `tests.xml`, `coverage.xml` y `htmlcov/index.html`.

## Publicación

GitHub Actions publica la imagen en GHCR al actualizar `main`:

```text
ghcr.io/vicenkks/backend-2026-grupo-05:latest
```

La ejecución automática de pruebas en CI y el despliegue en Kubero están pendientes. La comprobación de reservas superpuestas tampoco garantiza la exclusión ante solicitudes concurrentes.

## Documentación

- [Autenticación y pruebas](docs/auth-testing.md)
- [Modelo de datos](docs/modelo.md)
- [Problemática](docs/problematica.md)
- [Rúbrica](docs/rubrica_codigo.md)
- [Presentación](docs/presentacion.html)
- [Equipo y evidencias Git](docs/equipo.md)

## Integrantes

Vicente Huilcaman, Annan John, Alonso Astete y Matias Espinoza.
