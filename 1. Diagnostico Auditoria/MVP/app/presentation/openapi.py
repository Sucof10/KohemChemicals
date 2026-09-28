from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from app.application.dtos import UserCreateDTO, RawMaterialCreateDTO, RawMaterialUpdateDTO, OrderCreateDTO, OrderStatusUpdateDTO, AIChatRequestDTO


def _schema(model):
    return model.model_json_schema(ref_template="#/components/schemas/{model}")


def _set_dual_body(schema, path, method, model, example, form_examples=None):
    op = schema["paths"].get(path, {}).get(method)
    if not op:
        return
    ref = {"$ref": f"#/components/schemas/{model.__name__}"}
    form_schema = ref.copy()
    if form_examples:
        form_schema = {"type": "object", "properties": form_examples["properties"], "required": form_examples.get("required", [])}
    op["requestBody"] = {
        "required": True,
        "content": {
            "application/json": {
                "schema": ref,
                "example": example,
            },
            "application/x-www-form-urlencoded": {
                "schema": form_schema,
                "example": form_examples.get("example", {}) if form_examples else example,
            },
        },
    }


def configure_dual_body_openapi(app: FastAPI):
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        schema = get_openapi(title=app.title, version=app.version, description=app.description, routes=app.routes)
        schemas = schema.setdefault("components", {}).setdefault("schemas", {})
        # Los endpoints aceptan Request manualmente, por lo que FastAPI no siempre
        # registra sus modelos de entrada en components/schemas. Los registramos
        # explícitamente y, además, trasladamos los modelos anidados/$defs
        # (por ejemplo UserRole, OrderItemCreateDTO y OrderStatus) a components/schemas.
        # Esto evita errores Swagger del tipo: "Could not resolve reference".
        def register_model(model):
            model_schema = model.model_json_schema(
                ref_template="#/components/schemas/{model}"
            )
            for definition_name, definition_schema in model_schema.pop("$defs", {}).items():
                schemas[definition_name] = definition_schema
            schemas[model.__name__] = model_schema

        for model in (
            UserCreateDTO, RawMaterialCreateDTO, RawMaterialUpdateDTO,
            OrderCreateDTO, OrderStatusUpdateDTO, AIChatRequestDTO
        ):
            register_model(model)
        # Keep Pydantic-generated schemas and add explicit examples.
        form_register = {
            "properties": {
                "username": {"type": "string", "example": "analista1"},
                "email": {"type": "string", "format": "email", "example": "analista1@empresa.com"},
                "password": {"type": "string", "format": "password", "example": "AnalistaPass123!"},
                "role": {"type": "string", "enum": ["admin", "analista", "cliente"], "example": "analista"},
            },
            "required": ["username", "email", "password"],
            "example": {"username":"analista1","email":"analista1@empresa.com","password":"AnalistaPass123!","role":"analista"},
        }
        _set_dual_body(schema, "/api/v1/auth/register", "post", UserCreateDTO, form_register["example"], form_register)

        token_schema = {
            "type": "object",
            "properties": {
                "grant_type": {"type": "string", "enum": ["password"], "default": "password"},
                "username": {"type": "string", "example": "admin"},
                "password": {"type": "string", "format": "password", "example": "AdminPass123!"},
                "scope": {"type": "string", "default": ""},
                "client_id": {"type": "string", "nullable": True, "default": ""},
                "client_secret": {"type": "string", "format": "password", "nullable": True, "default": ""},
            },
            "required": ["username", "password"],
        }
        token_op = schema["paths"]["/api/v1/auth/token"]["post"]
        token_op["requestBody"] = {
            "required": True,
            "content": {
                "application/json": {"schema": token_schema, "example": {"grant_type":"password","username":"admin","password":"AdminPass123!","scope":"","client_id":"","client_secret":""}},
                "application/x-www-form-urlencoded": {"schema": token_schema, "example": {"grant_type":"password","username":"admin","password":"AdminPass123!","scope":"","client_id":"","client_secret":""}},
            },
        }

        _set_dual_body(schema, "/api/v1/materials", "post", RawMaterialCreateDTO,
            {"name":"Glicerina vegetal","category":"Humectantes","unit":"kg","price":18000,"stock":100,"description":"Materia prima para formulaciones cosméticas."},
            {"properties": {"name":{"type":"string","example":"Glicerina vegetal"},"category":{"type":"string","example":"Humectantes"},"unit":{"type":"string","example":"kg"},"price":{"type":"number","example":18000},"stock":{"type":"number","example":100},"description":{"type":"string","example":"Materia prima para formulaciones cosméticas."}},"required":["name","category","unit","price","stock"],"example":{"name":"Glicerina vegetal","category":"Humectantes","unit":"kg","price":"18000","stock":"100","description":"Materia prima para formulaciones cosméticas."}})
        _set_dual_body(schema, "/api/v1/materials/{material_id}", "put", RawMaterialUpdateDTO,
            {"name":"Glicerina vegetal refinada","price":19500,"stock":120,"description":"Materia prima actualizada."},
            {"properties":{"name":{"type":"string","example":"Glicerina vegetal refinada"},"category":{"type":"string","example":"Humectantes"},"unit":{"type":"string","example":"kg"},"price":{"type":"number","example":19500},"stock":{"type":"number","example":120},"description":{"type":"string","example":"Materia prima actualizada."}},"example":{"name":"Glicerina vegetal refinada","price":"19500","stock":"120","description":"Materia prima actualizada."}})
        _set_dual_body(schema, "/api/v1/orders", "post", OrderCreateDTO,
            {"items":[{"raw_material_id":1,"quantity":5},{"raw_material_id":2,"quantity":10}],"notes":"Pedido para formulación cosmética."},
            {"properties":{"items":{"type":"string","example":"[{\"raw_material_id\":1,\"quantity\":5},{\"raw_material_id\":2,\"quantity\":10}]"},"notes":{"type":"string","example":"Pedido para formulación cosmética."}},"required":["items"],"example":{"items":"[{\"raw_material_id\":1,\"quantity\":5}]","notes":"Pedido para formulación cosmética."}})
        _set_dual_body(schema, "/api/v1/orders/{order_id}/status", "patch", OrderStatusUpdateDTO,
            {"status":"confirmado"},
            {"properties":{"status":{"type":"string","enum":["pendiente","confirmado","preparando","enviado","entregado","cancelado"],"example":"confirmado"}},"required":["status"],"example":{"status":"confirmado"}})
        _set_dual_body(schema, "/api/v1/ai/chat", "post", AIChatRequestDTO,
            {"message":"Necesito asesoría para formular un producto cosmético."},
            {"properties":{"message":{"type":"string","example":"Necesito asesoría para formular un producto cosmético."}},"required":["message"],"example":{"message":"Necesito asesoría para formular un producto cosmético."}})
        app.openapi_schema = schema
        return app.openapi_schema
    app.openapi = custom_openapi
