"""Utilidades de validación de entrada para la capa de presentación.

Centraliza la conversión de errores de Pydantic y de cuerpos mal formados en
respuestas HTTP 422/400, en lugar de dejar que se conviertan en 500.
"""

import json

from fastapi import HTTPException, Request
from pydantic import ValidationError


def detalle_validacion(exc: ValidationError) -> list[dict]:
    return [
        {"campo": ".".join(str(parte) for parte in error["loc"]), "mensaje": error["msg"]}
        for error in exc.errors()
    ]


def validar_modelo(modelo, datos):
    try:
        return modelo.model_validate(datos)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=detalle_validacion(exc))


async def leer_cuerpo(request: Request) -> dict:
    """Devuelve el cuerpo como diccionario, aceptando JSON o formulario."""
    content_type = request.headers.get("content-type", "").split(";", 1)[0].lower()
    if content_type == "application/json":
        try:
            datos = await request.json()
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise HTTPException(status_code=400, detail="El cuerpo de la solicitud no es un JSON UTF-8 válido.")
        if not isinstance(datos, dict):
            raise HTTPException(status_code=422, detail="El cuerpo debe ser un objeto JSON.")
        return datos
    if content_type in ("application/x-www-form-urlencoded", "multipart/form-data"):
        return dict(await request.form())
    raise HTTPException(status_code=415, detail="Use application/json o application/x-www-form-urlencoded.")
