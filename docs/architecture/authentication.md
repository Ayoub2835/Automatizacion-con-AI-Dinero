# Autenticación (Fase 0/1)

## Flujo actual

1. **Registro** (`POST /api/v1/auth/register`): crea una `Organization`
   nueva y un `User` con rol `admin` dentro de ella. Es el flujo de "alta
   de una gestoría nueva en el sistema" — no hay invitación de usuarios
   adicionales todavía (ver "Pendiente" abajo).
2. **Login** (`POST /api/v1/auth/login`): valida email + contraseña
   (bcrypt) y devuelve un par de tokens JWT (`access_token`,
   `refresh_token`).
3. **Autenticación de requests**: `Authorization: Bearer <access_token>`.
   `app/api/deps.py::get_current_user` decodifica el JWT y carga el
   usuario. Cualquier endpoint que lo necesite lo declara como
   dependencia FastAPI (`Depends(get_current_user)`).

El email es único a nivel global del sistema (no por organización): un
usuario no necesita indicar a qué gestoría pertenece para iniciar sesión.

## Tokens

- Firmados con HS256 y `SECRET_KEY` (variable de entorno — **debe** ser
  distinta y secreta en cada entorno real, nunca el valor de
  `.env.example`).
- `access_token`: vida corta (`ACCESS_TOKEN_EXPIRE_MINUTES`, 30 min por
  defecto). Se envía en cada request.
- `refresh_token`: vida larga (`REFRESH_TOKEN_EXPIRE_DAYS`, 7 días por
  defecto). **Emitido pero sin endpoint de refresco todavía** — es un
  punto de extensión pendiente (ver abajo).

## Explícitamente pendiente (no construir sin necesidad confirmada)

- **Endpoint de refresh token** (`POST /api/v1/auth/refresh`): el token se
  emite pero no hay endpoint que lo consuma todavía.
- **Invitar usuarios a una organización existente**: hoy solo existe
  "crear una organización nueva con su primer admin".
- **Revocación de tokens** (logout del lado servidor, listas de
  revocación): con JWT sin estado, requiere una decisión explícita
  (blacklist en Redis, tokens de corta vida + rotación, etc.) que se toma
  cuando haga falta, no antes.
- **Recuperación de contraseña**.
- **Permisos granulares más allá de `admin`/`member`**.

Cada uno de estos, cuando se construya, debe documentarse aquí y su
decisión de diseño relevante como ADR si no es trivial.
