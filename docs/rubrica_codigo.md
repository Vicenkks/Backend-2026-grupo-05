# Evidencia por criterio de código

Esta matriz relaciona la implementación con la rúbrica; no sustituye la calificación del docente.

| Criterio | Implementación | Verificación reproducible |
|---|---|---|
| Ejecución y endpoints | Dockerfile, Compose, scripts/start.sh; 19 operaciones | Suite recorre las 19 combinaciones método/ruta con respuestas exitosas; arranque desde BD vacía. |
| Modelo del dominio | Cuatro entidades con UUID y al menos cuatro atributos adicionales; relaciones ORM 1:N | docs/modelo.md y creación/consulta de recursos relacionados. |
| REST, DTO y OpenAPI | Rutas plurales, DTO de entrada/salida y contrato con ejemplos y errores | GET /openapi.json; la suite comprueba las 19 operaciones y documentación. |
| CRUD y persistencia | CRUD de espacios, empresas y disponibilidades con SQLAlchemy | Crear/leer/actualizar/eliminar y reinicio real del proceso. |
| Validaciones y reglas | Longitud, números, enum, formato, referencias y reglas entre recursos | Casos 422, RUT inválido, duración mínima, empresa/espacio inactivo, fuera de horario y solapamiento. |
| HTTP y errores | 200/201/204/400/404/409/422; objeto error uniforme | Estados y claves JSON comprobados en cada solicitud de error. |
| Consulta combinada | /espacios filtra, ordena y pagina en SQL; total y total_paginas filtrados | Comparación de páginas consecutivas con límite 1 y capacidad descendente. |
| Capas | presentation, application, domain, infrastructure | README explica responsabilidades, transacción y recorrido router-servicio-repositorio-mapper-ORM-BD. |
| Migraciones y seeders | Alembic; carga inicial transaccional, dos o más ejemplos por entidad | Upgrade y check; seeding repetido; fallo intencional seguido de verificación de rollback total. |
| Pruebas | tests_manual/run_checks.py, casos.md, requests.http y results.json | 72 comprobaciones HTTP más migraciones, seeders, rollback y persistencia tras reinicio. |

## Requisitos que el grupo debe aportar

Nombres, responsabilidades reales, nombre del repositorio exigido, cinco commits significativos y una rama/PR por integrante. Los cambios técnicos no crean esas evidencias de participación. La presentación/defensa corresponde al otro 60% de la evaluación y requiere preparación independiente.

## Resumen de cambios por directorio

- Raíz: `Dockerfile`, `docker-compose.yml`, `.dockerignore`, `.python-version`, `.env.example`, `.gitignore` y `README.md`: contenedores, volumen persistente, healthcheck, configuración y ejecución reproducible.
- `scripts/start.sh`: migraciones, seeders e inicio de Uvicorn.
- `app/main.py`: carga inicial atómica y registro de errores/documentación.
- `domain/disponibilidad_domain.py`, `domain/errors.py`: UUID coherentes y errores independientes de HTTP.
- `application/services/`: identificadores, RUT normalizado, referencias, conflictos, fechas UTC, rango de reservas y orden de espacios.
- `infrastructure/database.py`: dotenv, conexión PostgreSQL con psycopg2 y configuración mediante variables.
- `infrastructure/mappers/`: correspondencia con los atributos actuales y reconstrucción UTC.
- `infrastructure/repositories/`: flush bajo transacción externa; filtros coherentes en conteos y ordenamiento estable.
- `infrastructure/seeders/`: RUT válidos, dos reservas futuras UTC y comando ejecutable; conservación de datos existentes.
- `presentation/dependencies.py`: commit/rollback por solicitud antes de enviar la respuesta.
- `presentation/routers/`: orden configurable y respuesta paginada completa.
- `presentation/schemas/dtos/`: límites coherentes, fechas con zona, alias compatible y total de páginas.
- `presentation/errors.py`, `presentation/openapi.py`: formato de errores y contrato documentado.
- `tests_manual/`: runner aislado, escenarios, solicitudes de demostración y resultados obtenidos.
- `docs/modelo.md`: diagramas de clases y datos; este documento vincula evidencia y criterios.

Se conserva la migración inicial: `alembic check` confirma correspondencia con los modelos. No se modificaron las declaraciones de dependencias, el lockfile ni la base histórica versionada.

## Validación realizada

- Local: 72 comprobaciones HTTP exitosas, migraciones y seeders repetibles.
- Dentro de Docker: las mismas 72 comprobaciones exitosas.
- Compose: construcción correcta, contenedor saludable y persistencia de volumen comprobada tras recrearlo.
- El registro de prueba creado para comprobar el volumen se eliminó al finalizar. La pila de desarrollo conserva sus datos.
- La primera descarga de dependencias en esta nube requirió la CA del proxy como secreto temporal de BuildKit y resolución del proxy; no se desactivó TLS ni se copiaron credenciales a la imagen.

Resultados: `tests_manual/results.json`, `tests_manual/results.docker.json` y `tests_manual/compose_results.json`.

La suite actual usa PostgreSQL y psycopg2 también al ejecutarse dentro de Docker. Los resultados anteriores a este cambio eran de SQLite; no deben presentarse como evidencia actual. Ver docs/problematica.md, docs/equipo.md y docs/defensa.md para la entrega y preparación oral.

El runner verifica que cada una de las 19 operaciones documentadas tenga al menos una respuesta exitosa; no basta contar rutas declaradas. Comprueba orden ascendente/descendente y metadatos de una página vacía. OpenAPI incluye descripciones y ejemplos por parámetro y operación.
