# Modelo del coworking

## Clases de dominio

```mermaid
classDiagram
class Espacio {
 UUID id
 string nombre
 TipoEspacio tipo
 int capacidad
 EstadoEspacio estado
 esta_disponible_para_reserva()
}
class Empresa {
 UUID id
 string nombre
 string rut
 string contacto
 bool activa
 puede_reservar()
}
class Disponibilidad {
 UUID id
 UUID espacio_id
 int dia_semana
 time hora_apertura
 time hora_cierre
 bool activa
 contiene(inicio, fin)
}
class Reserva {
 UUID id
 UUID espacio_id
 UUID empresa_id
 datetime fecha_inicio
 datetime fecha_fin
 EstadoReserva estado
 se_superpone_con(otra)
 cancelar(ahora)
}
Espacio "1" --> "0..*" Disponibilidad
Espacio "1" --> "0..*" Reserva
Empresa "1" --> "0..*" Reserva
```

## Modelo de datos persistido

```mermaid
erDiagram
 ESPACIOS ||--o{ DISPONIBILIDADES : tiene
 ESPACIOS ||--o{ RESERVAS : recibe
 EMPRESAS ||--o{ RESERVAS : realiza
 ESPACIOS {
  UUID id PK
  string nombre
  string tipo
  int capacidad
  string estado
 }
 EMPRESAS {
  UUID id PK
  string nombre
  string rut UK
  string contacto
  boolean activa
 }
 DISPONIBILIDADES {
  UUID id PK
  UUID espacio_id FK
  int dia_semana
  time hora_apertura
  time hora_cierre
  boolean activa
 }
 RESERVAS {
  UUID id PK
  UUID espacio_id FK
  UUID empresa_id FK
  datetime fecha_inicio
  datetime fecha_fin
  string estado
 }
```

Cada disponibilidad/reserva requiere su espacio; cada reserva requiere su empresa. Existen relaciones 1:N tanto en claves foráneas como en `relationship(back_populates=...)`. La API verifica referencias y la BD impide borrados que dejarían registros huérfanos. Las reservas canceladas conservan las relaciones y el historial.

La migración inicial crea UUID, restricciones de capacidad, estados, horarios y fechas; índice único de RUT e índices de consultas de reservas por empresa/espacio y fechas.
