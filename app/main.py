# app/main.py
from .adapters.controllers.api import app

if __name__ == "__main__":
    if not hasattr(app, "openapi_schema") or app.openapi_schema is None:
        openapi_schema = app.openapi()
    else:
        openapi_schema = app.openapi_schema
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    openapi_schema["security"] = [{"OAuth2PasswordBearer": []}]
    app.openapi_schema = openapi_schema
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
