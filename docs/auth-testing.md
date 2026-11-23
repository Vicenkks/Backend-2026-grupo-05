# Autenticación y pruebas

Implementación para la pauta final, secciones 5.5–5.7. No incluye el pipeline ni despliegue en Kubero.

## Permisos y rutas

Las cuentas nuevas tienen rol de lector y solo pueden consultar datos. Un administrador gestiona
espacios, empresas, disponibilidades y reservas. Los lectores consultan todos los recursos;
son usuarios internos, no clientes aislados por empresa. Un cliente no puede seleccionar
su rol, estado o versión de token en el DTO de registro.

Rutas públicas: POST /auth/registro, /auth/login, /auth/recuperacion y /auth/restablecer.
GET /auth/me requiere Authorization: Bearer <access_token>.
POST /auth/refresh y /auth/logout requieren cookie refresh_token.
Las 19 rutas de negocio requieren Bearer; sus escrituras requieren administrador.
/docs, /openapi.json y /health son públicos. /health no devuelve información sensible.

Registro/login: JSON con email y password. Recuperación: JSON con email.
Restablecimiento: POST al reset_link recibido, con JSON que contiene password.
También admite token y password en el cuerpo; no acepta un ID de usuario aparte.
Email se normaliza a minúsculas. El registro rechaza duplicados mediante validación
y restricción única en PostgreSQL. Registro y restablecimiento exigen 12–128 caracteres.

## Credenciales y tokens

- Argon2id con los parámetros predeterminados de argon2-cffi. La contraseña no se guarda tal como se escribió.
- Access JWT HS256, duración 15 minutos. Verifica firma, algoritmo, issuer, audience,
  sub UUID, exp, iat, propósito y versión. JWT_SECRET no tiene valor predeterminado y
  requiere al menos 32 bytes; usar un valor largo y aleatorio.
- Cada petición autenticada consulta el estado y versión actuales de la cuenta.
- Refresh opaco aleatorio de 48 bytes; solo SHA-256 se guarda en PostgreSQL. Familia
  con duración absoluta de siete días. Cada renovación consume el token y crea otro.
  Reutilizar un token usado/revocado revoca toda su familia, incluso tras rollback HTTP.
- Logout revoca la familia de refresh, pero el access emitido dura hasta exp.
  Un cambio de contraseña sí invalida de inmediato access y refresh anteriores.
- Cinco intentos de login por identificador cada quince minutos, incluidos los exitosos.
  Las cuentas desconocidas realizan una verificación Argon2 equivalente. Los errores de
  login son genéricos y los contadores persisten aunque la respuesta sea 401.
- Tres solicitudes de recuperación por identificador cada quince minutos. Se responde
  202 genérico para cuentas conocidas, desconocidas o limitadas. Este límite no bloquea login.
- Token JWT exclusivo de recuperación con jti persistido, duración 15 minutos y uso único.
  El cambio de hash, incremento de versión, consumo e invalidación de sesiones se confirman
  en una transacción. Se rechaza la contraseña anterior como nueva contraseña.
- Recuperación devuelve reset_link en JSON. Cuentas desconocidas o limitadas reciben
  un enlace con el mismo formato, pero sin un registro válido para restablecer.

Los contadores son compartidos en PostgreSQL. Los límites por identificador no reemplazan
un control global/IP de volumen en el proxy si la API se expone masivamente. La eliminación
periódica de registros vencidos puede añadirse al operar a largo plazo; no eliminar tokens
consumidos mientras su familia pueda seguir vigente, porque se utilizan para detectar replay.

## Cookies y navegador

Refresh: HttpOnly, SameSite=Strict, Path=/auth, Secure por defecto.
COOKIE_SECURE=false solamente para desarrollo HTTP. Se comprueba Origin cuando está
presente y CORS permite únicamente ALLOWED_ORIGINS explícitos, nunca '*'.
Logout y refresh solo requieren la cookie refresh_token que envía el navegador.
No hay que rellenar ningún campo adicional para cerrar o renovar la sesión.
Swagger autoriza automáticamente al completar login/refresh.
Logout/restablecimiento limpian el Bearer de Swagger. Al recargar la página se pierde
el Bearer en memoria: ejecutar refresh o iniciar sesión de nuevo.
Otros clientes deben enviar Bearer y, para refresh/logout, la cookie refresh_token.
No copiar tokens a Git, logs, capturas públicas ni reportes.

## Recuperar y restablecer desde Swagger

1. Ejecutar POST /auth/recuperacion con `{"email":"persona@example.com"}`.
2. La respuesta 202 incluye `reset_link`, por ejemplo
   `http://localhost:8000/auth/restablecer?token=...`.
3. En POST /auth/restablecer, colocar el valor después de `token=` en el parámetro
   token y enviar `{"password":"Otra-clave-segura-2026"}`. También puede enviarse
   un POST directamente al enlace con ese mismo JSON; abrirlo en una pestaña hace
   un GET y no restablece la contraseña.
4. Iniciar sesión con la contraseña nueva. El enlace solo permite un uso y vence
   a los quince minutos.

Este mecanismo es una demostración académica: devolver la credencial de recuperación
sin verificar la identidad no es apto para cuentas reales en una API pública.
No se necesita Mailpit ni SMTP. La pauta 5.6 permite el enlace en JSON; la prueba
adapta el paso de correo descrito en 5.7 a este mecanismo.

## Preparación local

1. `uv sync --frozen` y copiar `.env.example` a `.env` si todavía no existe.
2. Generar JWT_SECRET localmente y configurarlo en `.env`.
3. `docker compose up --build -d --wait` aplica migraciones y seeders existentes.
4. Registrar cuentas desde `/docs`. No hay administrador predeterminado.
5. `docker compose exec api python -m scripts.set_role persona@example.com admin`.
6. Iniciar sesión después del cambio de rol; el comando invalida sesiones anteriores.

Fuera de Docker: `uv run python -m scripts.set_role persona@example.com admin` utiliza
la misma conexión configurada en `.env`. Para volver al rol de lector, cambia admin por lector en el comando.

## Recorrido y archivos

presentation/routers/auth_router.py recibe DTO y delega a AuthService. Las dependencias
HTTP en presentation/security/auth.py manejan Bearer, cookies y permisos.
application/services/auth_service.py coordina registro, acceso y recuperación.
domain/auth.py define identidad, política de contraseña y permiso administrativo.
infrastructure/security encapsula Argon2 y JWT; auth_repository.py encapsula SQL.
La dependencia compartida get_session confirma o revierte la transacción.
Los intentos fallidos y la revocación por replay se confirman expresamente antes del 401.
La migración 7a01_auth agrega tablas sin alterar datos de negocio existentes.

## Tres niveles de pruebas

`make test-unit`: dominio, contraseñas, tokens, DTO, permisos y servicios con dobles.
No necesita Docker, BD ni correo. Incluye errores, valores límite y llamadas esperadas.

`make test-integration`: PostgreSQL real con migraciones; unicidad, claves foráneas,
rotación, revocación persistente, intentos, recuperación y solicitudes simultáneas.
Se verifica el límite mediante los registros persistidos y el rechazo de enlaces inválidos.

`make test-e2e`: Uvicorn en un proceso separado y HTTPX por TCP, PostgreSQL real y
enlaces de recuperación obtenidos por HTTP. No reemplaza servicios, JWT ni repositorios.
Incluye los tres flujos de la pauta:

1. Registro → asignar rol de administrador → login → crear/consultar → logout → refresh rechazado.
2. Solicitud → enlace JSON → cambio → segundo uso y contraseña vieja rechazados → nuevo login;
   access y refresh anteriores se rechazan.
3. Sin credencial: 401 → lector: 403 → admin: misma operación exitosa y consulta del resultado.

Adicionalmente verifica JWT vencido/manipulado/de otro propósito, CORS, cuenta inactiva,
no autoasignación de permisos, recuperación inválida y replay de refresh. Las 72 comprobaciones
HTTP anteriores de negocio se conservan dentro de un caso de regresión que inicia y reinicia
su propia API. Se usan fechas preparadas; no hay esperas manuales para vencer tokens.

`make test` ejecuta todo y genera JUnit, XML y HTML de cobertura. Falla ante errores o
cobertura inferior a 85 %. Se instrumentan también los subprocesos Uvicorn y la regresión.
El porcentaje combina líneas y ramas de todo el código propio de app/domain/application/
infrastructure/presentation; no se limita a auth. Migraciones se ejecutan y verifican con
Alembic, pero no forman parte del porcentaje. Los reportes están en reports/ (ignorado en Git).

La BD de tests usa el puerto 55432, usuario coworking_test y contraseña exclusiva de test.
Cada ejecución crea bases aleatorias y elimina únicamente esas bases al terminar.
`make test-down` baja solo Compose de test. Ningún test usa la BD de desarrollo de `.env`.
No correr dos suites simultáneamente contra el mismo entorno de test.

Los reportes JSON guardados anteriormente en tests_manual son históricos. Para nueva
evidencia usar el reporte de make test y asociarlo al commit que se entregue.

## Límites de este cambio

No implementa CI/CD, Kubero, frontend ni aislamiento entre empresas. No resuelve la carrera
preexistente de reservas simultáneas de negocio. Refresh y recuperación sí se serializan
por usuario con bloqueo de PostgreSQL y tienen pruebas de concurrencia.
La presentación final y las evidencias de trabajo individual deben completarse por el grupo.
