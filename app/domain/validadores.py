def validar_texto(valor: str, nombre_campo: str) -> str:
    #Valida que un texto no esté vacío y lo retorna limpio.
    if not valor or not str(valor).strip():
        raise ValueError(f"El {nombre_campo} es obligatorio")
    return str(valor).strip()