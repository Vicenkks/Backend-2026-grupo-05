# Problemática y alcance — propuesta académica

La siguiente formulación describe el escenario que modela el proyecto; no afirma que se haya realizado una investigación de usuarios.

## P1. Situación

En el escenario propuesto, la administración de un coworking recibe solicitudes de reserva por canales separados y registra horarios sin una verificación central de disponibilidad. Dos solicitudes pueden apuntar al mismo espacio y horario.

## P2. Actores

- Administración del coworking: registra espacios, horarios y empresas; consulta y mantiene las reservas.
- Representantes de empresas: solicitan espacios y necesitan conocer o cancelar sus reservas.

Son actores del problema, no roles autenticados implementados en esta versión.

## P3. Consecuencias

- Reservas incompatibles obligan a reprogramar reuniones o cambiar de sala.
- Consultar registros separados consume tiempo y facilita errores de disponibilidad.

## P4. Información administrada

Espacios (nombre, tipo, capacidad, estado), empresas (nombre, RUT, contacto, activa), disponibilidades (espacio, día, apertura, cierre, activa) y reservas (espacio, empresa, inicio, fin, estado). Las primeras tres entidades admiten CRUD; las reservas se crean, consultan y cancelan conservando historial.

## P5. Requisitos funcionales

1. El sistema debe permitir crear y consultar espacios.
2. El sistema debe permitir modificar capacidad, tipo y estado de los espacios.
3. El sistema debe permitir eliminar espacios sin referencias relacionadas.
4. El sistema debe permitir registrar empresas con RUT válido y único.
5. El sistema debe permitir actualizar y consultar empresas.
6. El sistema debe permitir definir horarios semanales por espacio.
7. El sistema debe permitir reservar espacios activos para empresas activas dentro de sus horarios.
8. El sistema debe permitir rechazar reservas de menos de 30 minutos o superpuestas.
9. El sistema debe permitir consultar espacios filtrando, ordenando y paginando.
10. El sistema debe permitir cancelar reservas futuras conservando su historial.
11. El sistema debe permitir recuperar datos después de reiniciar la API.

## P6. Exclusiones

- Autenticación y permisos por actor.
- Pagos, facturación y tarifas.
- Frontend y notificaciones.
- Garantía de exclusión de reservas frente a escrituras simultáneas de múltiples procesos.

## P7. Criterios de aceptación

| Criterio | Verificación |
|---|---|
| Crear un espacio válido devuelve 201 y un UUID recuperable | CRUD en run_checks.py. |
| Capacidad cero o estado desconocido devuelve 422 uniforme | Casos de validación. |
| Una reserva de 15 minutos devuelve 400 | Caso de duración mínima. |
| Una segunda reserva superpuesta devuelve 409 | Caso de conflicto. |
| Una referencia inexistente devuelve 404 | Casos de UUID ausente. |
| El GET de espacios filtra, ordena y pagina con total coherente | Comparación de dos páginas. |
| Un espacio actualizado y una reserva sobreviven al reinicio | El runner detiene y vuelve a iniciar Uvicorn. |
| La preparación de una base vacía carga todas las entidades | Migraciones, seeders repetidos y conteos. |
