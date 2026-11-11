"""P10 — Regresión y consistencia de la arquitectura Onion.

Ejecuta la suite completa y audita estáticamente las dependencias entre capas:
el dominio no debe conocer FastAPI, SQLAlchemy, MCP ni Pydantic, y la
aplicación no debe importar infraestructura ni frameworks.
"""

import ast
import subprocess
import sys
from pathlib import Path

RAIZ_MVP = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ_MVP))

from _common import EVIDENCIAS, guardar, imprimir

PROHIBIDOS = {
    "domain": {"fastapi", "starlette", "sqlalchemy", "mcp", "pydantic", "aiosqlite", "jose", "passlib"},
    "application": {"fastapi", "starlette", "sqlalchemy", "mcp", "aiosqlite", "jose", "passlib"},
}


def _imports(archivo: Path) -> set[str]:
    arbol = ast.parse(archivo.read_text(encoding="utf-8"))
    modulos = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            modulos.update(alias.name.split(".")[0] for alias in nodo.names)
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            modulos.add(nodo.module.split(".")[0])
    return modulos


def _auditar_capa(capa: str) -> list[dict]:
    hallazgos = []
    for archivo in sorted((RAIZ_MVP / "app" / capa).rglob("*.py")):
        violaciones = sorted(_imports(archivo) & PROHIBIDOS[capa])
        if violaciones:
            hallazgos.append(
                {
                    "archivo": str(archivo.relative_to(RAIZ_MVP)).replace("\\", "/"),
                    "imports_prohibidos": violaciones,
                }
            )
    return hallazgos


def ejecutar() -> dict:
    suite = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=RAIZ_MVP,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    colecta = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q"],
        cwd=RAIZ_MVP,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    ultima_linea = [linea for linea in suite.stdout.strip().splitlines() if linea.strip()][-1]

    evidencias = {
        "pytest": {
            "codigo_salida": suite.returncode,
            "resumen": ultima_linea,
            "salida": suite.stdout,
            "errores": suite.stderr[-2000:],
        },
        "pruebas_colectadas": [
            linea for linea in colecta.stdout.splitlines() if "::" in linea
        ],
        "arquitectura": {
            "domain": _auditar_capa("domain"),
            "application": _auditar_capa("application"),
        },
    }
    evidencias["criterios"] = {
        "dominio_puro": not evidencias["arquitectura"]["domain"],
        "aplicacion_sin_frameworks": not evidencias["arquitectura"]["application"],
        "suite_ejecutable": "error" not in ultima_linea.lower(),
    }
    return evidencias


if __name__ == "__main__":
    resultado = ejecutar()
    imprimir("P10 — Regresión y arquitectura", {
        "pytest": {k: v for k, v in resultado["pytest"].items() if k != "salida"},
        "arquitectura": resultado["arquitectura"],
        "criterios": resultado["criterios"],
    })
    guardar("f10_regresion.json", resultado)
    (EVIDENCIAS / "f10_pytest.txt").write_text(
        resultado["pytest"]["salida"], encoding="utf-8"
    )
