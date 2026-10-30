# Presentación — 10 minutos y 5 minutos de preguntas

Guion de 10 diapositivas exportable a la herramienta de presentación del grupo. Completar integrantes antes de presentar. Usar texto grande, alto contraste y etiquetas escritas para éxitos/errores. Cada integrante debe ensayar toda la exposición de forma autónoma.

## 1. Problema y actores — 0:00 a 0:45

Reservas coordinadas por canales separados pueden superponerse. Actores: administración del coworking y representantes de empresas. Explicar dos consecuencias: reprogramaciones y tiempo perdido al buscar disponibilidad.

## 2. Alcance y aceptación — 0:45 a 1:30

Mostrar los requisitos de docs/problematica.md: administrar cuatro entidades, reservar y cancelar, consultar con filtros y conservar datos. Excluir pagos, autenticación y frontend. Señalar cinco criterios de aceptación y cómo se prueban.

## 3. Dominio — 1:30 a 2:15

Mostrar el diagrama de clases de docs/modelo.md. Cada entidad posee UUID y al menos cuatro atributos útiles. Un espacio tiene muchas disponibilidades y reservas; una empresa tiene muchas reservas.

## 4. Reglas y validaciones — 2:15 a 3:00

Distinguir tipo/formato de reglas de negocio. Ejemplos: capacidad positiva y UUID; duración mínima, espacio activo y ausencia de solapamiento. Relacionar cada regla con su caso reproducible.

## 5. Contrato y cuatro capas — 3:00 a 4:00

Abrir Swagger. Explicar DTO de entrada/salida, 201/204 y errores uniformes. Seguir POST /reservas: router → servicio → repositorios → mappers → SQLAlchemy → PostgreSQL. La dependencia confirma o revierte la transacción.

## 6. Persistencia y preparación — 4:00 a 5:00

Mostrar docker compose ps y alembic current/check. Explicar PostgreSQL 16, psycopg2 y volumen postgres_data. Enseñar seeders, transacción y al menos dos ejemplos por entidad. La suite prepara bases nuevas y prueba rollback.

## 7. Demostración HTTP — 5:00 a 6:30

Ejecutar desde tests_manual/requests.http: GET empresas (200), POST espacio (201), POST con capacidad cero (422) y GET espacios con filtro, orden y paginación (200). Comparar códigos y cuerpos; no depender de colores.

## 8. Reinicio y evidencia — 6:30 a 8:15

Consultar el espacio recién creado, ejecutar docker compose restart api, esperar el healthcheck y volver a consultar su mismo UUID. Mostrar results.json: motor PostgreSQL, casos esperado/obtenido y persistencia. Explicar que run_checks.py crea y elimina solo sus dos bases aleatorias. Ejecutar la suite antes de la defensa y tenerla preparada para repetirla si se solicita.

## 9. Decisiones y limitaciones — 8:15 a 9:15

Justificar ORM, migraciones, PostgreSQL y separación de capas. Limitación: el control de solapamientos consulta antes de insertar; varios procesos concurrentes necesitarían bloqueo o restricción de exclusión. Mejoras futuras: autenticación por roles y control de concurrencia. No afirmar que están implementadas.

## 10. Cierre y criterios de aceptación — 9:15 a 10:00

Relacionar la demostración con los criterios de aceptación y localizar las evidencias. Explicar qué necesidades cubre la versión y qué queda fuera del alcance.

## Ensayo y preguntas — después de la exposición

Sortear a la persona que expone; el resto participa en preguntas. Cronometrar 10 minutos y reservar 5 para preguntas. Practicar: ¿dónde se valida una referencia?, ¿qué hace un mapper?, ¿cuándo hay rollback?, ¿qué conserva el volumen?, ¿por qué 409 y no 400?, ¿cómo se evita afectar la BD de desarrollo en pruebas?, ¿cómo se calcula total_paginas?

Registrar el ensayo real: fecha, persona sorteada, duración, preguntas falladas y correcciones. No marcarlo completado sin realizarlo.
