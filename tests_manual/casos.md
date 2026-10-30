# Casos reproducibles y aislamiento

Ejecutar `uv run --frozen python tests_manual/run_checks.py` desde la raíz. No requiere una API iniciada. Requiere PostgreSQL disponible y DB_HOST, DB_PORT, DB_USER y DB_PASSWORD configurados; el usuario necesita CREATEDB. Requiere las dependencias instaladas y un puerto local libre. Cada ejecución usa un directorio temporal y dos bases PostgreSQL de nombre aleatorio; su servidor se detiene incluso ante fallos. Los resultados completos con cuerpos y estados se escriben en `results.json` con estado `passed` al completar toda la suite o `failed` si falla alguna comprobación. Revisar también el estado de salida del comando.

| Caso | Entrada / procedimiento | Resultado esperado |
|---|---|---|
| Preparación | BD vacía, upgrade head, alembic check, seed dos veces | Esquema vigente; cinco espacios, tres empresas, horarios y dos reservas; sin duplicados. |
| Contrato | GET /openapi.json | 19 operaciones, resumen, descripción y errores documentados. |
| CRUD | Crear, listar, consultar, actualizar y eliminar espacios/empresas/disponibilidades | 201, 200, 204; recuperación de campos actualizados. |
| Validación | Capacidad cero, nombre vacío/largo, enum inválido, fecha sin zona | 422 con estructura error uniforme y detalle del campo. |
| Inexistente | GET con UUID válido inexistente; creación con referencia ausente | 404, RESOURCE_NOT_FOUND. |
| Negocio | Reserva de 15 minutos, empresa inactiva, apertura posterior al cierre | 400, BUSINESS_RULE_VIOLATION. |
| Conflicto | RUT equivalente con puntuación, reserva superpuesta, cancelar dos veces | 409, CONFLICT. |
| Consulta | Tipo oficina, capacidad descendente, límite 1, páginas 1 y 2 | Elementos filtrados, ordenados, distintos; total y total_paginas coherentes. |
| Rango de fechas | GET reservas con empresa, desde y hasta | Items y total usan el mismo filtro. |
| Integridad | Eliminar empresa/espacio con relaciones | 409; la operación se revierte. |
| Persistencia | Actualizar espacio, crear reserva, detener y arrancar otro proceso | Mismos ID/campos y conteos; seeders no duplican. |
| Cancelación | Reserva futura confirmada → cancelar | 200, estado cancelada persistido; segunda solicitud 409. |

Las fechas de las pruebas se calculan a futuro y su disponibilidad se crea para el día correspondiente. Los UUID se obtienen de respuestas reales. El script comprueba ambos códigos y contenido, no solo disponibilidad de un puerto.
