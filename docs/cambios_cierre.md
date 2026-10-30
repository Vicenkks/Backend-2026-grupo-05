# Cierre de pendientes de la rúbrica

Base revisada: main, commit e32e9fe. Rama de trabajo: feat/cierre-rubrica.

| Archivos | Cambio |
|---|---|
| tests_manual/run_checks.py y postgres_fixture.py | Pruebas reales en PostgreSQL/psycopg2, dos bases de nombre aleatorio por ejecución, limpieza incluso ante fallos. |
| tests_manual/check_compose.py | Prueba reproducible de creación, recreación de API, recuperación del registro y eliminación del registro propio. |
| tests_manual/results.json y results.docker.json | Evidencias actuales: 72 comprobaciones HTTP aprobadas en local y 72 dentro de Docker, ambas con PostgreSQL. |
| tests_manual/compose_results.json | Evidencia PostgreSQL del registro conservado al recrear la API. |
| docker-compose.yml | API_PORT y DB_PORT configurables; Adminer opcional sin nombre fijo que impida usar otro proyecto. |
| README.md, tests_manual/casos.md, docs/rubrica_codigo.md | Documentación coherente con PostgreSQL, permisos de pruebas, aislamiento y comandos reproducibles. |
| docs/problematica.md | P1–P7: situación, actores, consecuencias, datos, once requisitos, exclusiones y ocho criterios comprobables. |
| docs/defensa.md y presentacion.html | Guion de 10 minutos, diez diapositivas navegables/imprimibles y preguntas de ensayo. |
| docs/equipo.md | Registro explícito de información y evidencias individuales pendientes. |

Validación: migraciones desde cero, esquema sin diferencias, seeders repetidos, rollback ante fallo inyectado, 19 operaciones HTTP, CRUD, reglas, errores, consultas y reinicio real de API. Las bases aleatorias de prueba se eliminaron (cero bases coworking_test_* restantes). La comprobación Compose preservó PostgreSQL y sus demás datos.

El alcance de este cierre es técnico; la composición del equipo queda fuera por indicación del usuario.

Los cambios se agrupan en la rama feat/cierre-rubrica para su revisión e integración en main. No se ha renombrado el repositorio.

Última revisión: OpenAPI específico por operación/parámetro; cobertura exitosa explícita de las 19 operaciones; páginas vacías y orden ascendente; reporte y limpieza de la comprobación Compose también ante fallos.
