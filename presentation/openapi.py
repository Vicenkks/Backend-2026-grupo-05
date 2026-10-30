from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: list = Field(default_factory=list)


class ErrorResponse(BaseModel):
    error: ErrorDetail


EXAMPLES = {
    "espacios": {"nombre": "Sala Norte", "tipo": "sala_reunion", "capacidad": 8, "estado": "activo"},
    "empresas": {"nombre": "Empresa Demo", "rut": "111111111", "contacto": "demo@example.test", "activa": True},
    "disponibilidades": {"espacio_id": "00000000-0000-4000-8000-000000000001", "dia_semana": 0, "hora_apertura": "09:00:00", "hora_cierre": "18:00:00", "activa": True},
    "reservas": {"espacio_id": "00000000-0000-4000-8000-000000000001", "empresa_id": "00000000-0000-4000-8000-000000000002", "fecha_inicio": "2035-01-08T10:00:00Z", "fecha_fin": "2035-01-08T11:00:00Z"},
}


def configure_openapi(app):
    """Complete the executable contract without placing business rules in routers."""
    from fastapi.openapi.utils import get_openapi

    def schema():
        if app.openapi_schema:
            return app.openapi_schema
        document = get_openapi(title=app.title, version="1.0.0", routes=app.routes,
            description="API de reservas de coworking. Horarios y reservas se interpretan en UTC. Aplicar migraciones antes del inicio.")
        error_schema = ErrorResponse.model_json_schema(ref_template="#/components/schemas/{model}")
        components = document.setdefault("components", {}).setdefault("schemas", {})
        components.update(error_schema.pop("$defs", {}))
        components["ErrorResponse"] = error_schema
        for path, operations in document["paths"].items():
            entity = path.strip("/").split("/")[0]
            for method, operation in operations.items():
                singular = {"espacios": "espacio", "empresas": "empresa", "disponibilidades": "disponibilidad", "reservas": "reserva"}[entity]
                if path.endswith("/cancelar"):
                    summary = "Cancelar una reserva futura"
                    description = "Conserva el registro y cambia su estado a cancelada. Devuelve 404 si no existe, 409 si ya fue cancelada y 400 si ya comenzó."
                elif method == "get" and "{" in path:
                    summary = f"Obtener {singular} por UUID"
                    description = f"Recupera un registro de {entity} desde PostgreSQL. Devuelve 404 si el UUID válido no existe y 422 si su formato no es válido."
                elif method == "get":
                    summary = f"Listar {entity} con filtros y paginación"
                    filters = {
                        "espacios": "tipo y estado. ordenar_por acepta nombre, capacidad, tipo o estado; direccion admite asc o desc. El UUID desempata el orden",
                        "empresas": "activa; se ordena por nombre y UUID",
                        "disponibilidades": "espacio_id, dia_semana y activa; se ordena por día, apertura y UUID",
                        "reservas": "espacio_id, empresa_id, estado, desde y hasta (inicio inclusivo con zona horaria); se ordena por inicio y UUID",
                    }
                    description = f"Filtra por {filters[entity]}. pagina comienza en 1; limite admite 1 a 100. total y total_paginas corresponden al filtro, incluso si la página está vacía."
                elif method == "post":
                    summary = f"Crear {singular}"
                    description = {
                        "espacios": "Registra un espacio con nombre de 1 a 100 caracteres, capacidad positiva y tipo/estado permitidos. Devuelve 201 con UUID generado.",
                        "empresas": "Valida el dígito verificador del RUT y normaliza puntuación. Devuelve 201; RUT inválido produce 400 y RUT duplicado 409.",
                        "disponibilidades": "Define un horario semanal UTC para un espacio existente. Día entre 0 y 6; cierre posterior a apertura. Referencia inexistente: 404; horario incoherente: 400.",
                        "reservas": "Requiere empresa y espacio activos, fechas con zona horaria y duración mínima de 30 minutos, dentro del mismo día y horario disponible UTC. Referencias ausentes: 404; regla incumplida: 400; superposición de empresa o espacio: 409.",
                    }[entity]
                elif method == "put":
                    summary = f"Actualizar {singular}"
                    description = "Reemplaza todos los atributos editables usando el esquema de entrada. Conserva el UUID. Un recurso inexistente produce 404; los campos inválidos producen 422. Se aplican las reglas de creación."
                else:
                    summary = f"Eliminar {singular}"
                    description = "Elimina el registro y devuelve 204 sin cuerpo. Si no existe devuelve 404. Las referencias existentes impiden borrar espacios y empresas (409); no se eliminan reservas en cascada."
                operation["summary"] = summary
                operation["description"] = description
                if entity in ("disponibilidades", "reservas") and method in ("post", "put"):
                    operation["description"] += " Los UUID de los ejemplos son ilustrativos: obtener valores reales con GET /espacios y GET /empresas. La secuencia ejecutable tests_manual/run_checks.py crea sus referencias y calcula fechas futuras automáticamente."
                for status, description in {"400": "Regla de negocio incumplida", "404": "Recurso inexistente", "409": "Conflicto de estado o referencias", "422": "Entrada inválida"}.items():
                    operation["responses"][status] = {"description": description, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}}
                example = EXAMPLES[entity]
                if "requestBody" in operation:
                    operation["requestBody"]["content"]["application/json"]["example"] = example
                for param in operation.get("parameters", []):
                    name = param["name"]
                    descriptions = {
                        "pagina": ("Número de página, desde 1.", 1),
                        "limite": ("Registros por página, entre 1 y 100.", 10),
                        "ordenar_por": ("Atributo de espacio usado para ordenar; UUID desempata.", "capacidad"),
                        "direccion": ("Sentido del orden: asc o desc.", "desc"),
                        "tipo": ("Tipo de espacio requerido.", "oficina"),
                        "estado": ("Estado permitido del recurso.", "confirmada" if entity == "reservas" else "activo"),
                        "activa": ("Conservar registros activos o inactivos.", True),
                        "dia_semana": ("Día UTC: lunes 0 a domingo 6.", 0),
                        "desde": ("Inicio de reserva mayor o igual a esta fecha con zona horaria.", "2035-01-08T00:00:00Z"),
                        "hasta": ("Inicio de reserva menor o igual a esta fecha con zona horaria.", "2035-01-09T00:00:00Z"),
                    }
                    description, example_value = descriptions.get(name, ("UUID de un recurso existente; obtenerlo del GET de su colección.", "00000000-0000-4000-8000-000000000001"))
                    param["description"] = description
                    param["example"] = example_value
                for status, data in operation["responses"].items():
                    if status in ("400", "404", "409", "422"):
                        data.setdefault("content", {}).setdefault("application/json", {})["example"] = {
                            "error": {"code": {"400":"BUSINESS_RULE_VIOLATION", "404":"RESOURCE_NOT_FOUND", "409":"CONFLICT", "422":"VALIDATION_ERROR"}[status], "message": data["description"], "details": []}}
                    elif status != "204":
                        item = {"id": "00000000-0000-4000-8000-000000000003", **example}
                        if entity == "reservas": item["estado"] = "cancelada" if path.endswith("/cancelar") else "confirmada"
                        data.setdefault("content", {}).setdefault("application/json", {})["example"] = (
                            {"items": [item], "total": 1, "pagina": 1, "limite": 10, "total_paginas": 1}
                            if method == "get" and "{" not in path else item)
        app.openapi_schema = document
        return document
    app.openapi = schema
