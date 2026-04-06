import time
import uuid

from fastapi import Depends, FastAPI, Request
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse, JSONResponse
from openai import APITimeoutError
from sqlalchemy.exc import SQLAlchemyError
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler

from app.auth.dependencies import get_current_user
from app.core.logging import (
    configure_logging,
    execution_time_var,
    get_logger,
    request_id_var,
    tenant_id_var,
)
from app.core.rate_limit import limiter
from app.db.models import User
from app.routers.billing import router as billing_router
from app.routers.export import router as export_router
from app.routers.flash import router as flash_router
from app.routers.health import router as health_router
from app.routers.stimuli import router as stimuli_router
from app.services.flashcards import AIServiceTimeoutError


configure_logging()
logger = get_logger("stimuli.api")

API_DESCRIPTION = """
The Micro-Learning Flash API powers stimul.li's AI-first learning workflows.

Use this API to transform long-form text into compact, high-signal learning objects,
including flashcards, prompts, and structured study stimuli optimized for rapid review.

Built for commercial SaaS integrations, the API supports authenticated access, usage-aware
billing, operational observability, and production deployment behind a secure reverse proxy.

## Getting Started

Teachers can get started in minutes:

1. Create a stimul.li account at `https://stimul.li`.
2. Open the developer dashboard and create your first API key.
3. Copy that key and send it in the `X-API-Key` header on every request.
4. Start by calling `/health` to verify connectivity, then use `/flash` to generate your first micro-learning cards.

If you need help getting classroom or district access set up, contact `support@stimul.li`.
""".strip()

CONTACT_INFO = {
    "name": "stimul.li API Support",
    "url": "https://docs.stimul.li",
    "email": "support@stimul.li",
}

LOGO_URL = "https://docs.stimul.li/static/stimuli-logo.png"
FAVICON_URL = "https://docs.stimul.li/static/stimuli-favicon.png"
SWAGGER_CUSTOM_CSS = """
<style>
  :root {
    --stimuli-blue: #1A5276;
    --stimuli-blue-dark: #154360;
    --stimuli-ink: #122230;
    --stimuli-surface: #f7fbfd;
    --stimuli-border: #d7e4ea;
  }

  body,
  .swagger-ui {
    background: linear-gradient(180deg, #f7fbfd 0%, #eef5f8 100%);
    color: var(--stimuli-ink);
  }

  .swagger-ui .topbar {
    background: linear-gradient(90deg, var(--stimuli-blue-dark) 0%, var(--stimuli-blue) 100%);
    border-bottom: 1px solid rgba(255, 255, 255, 0.12);
    padding: 12px 0;
  }

  .swagger-ui .topbar .download-url-wrapper {
    display: none;
  }

  .swagger-ui .info {
    margin: 32px 0;
  }

  .swagger-ui .info .title,
  .swagger-ui .opblock-tag,
  .swagger-ui .scheme-container .schemes-title {
    color: var(--stimuli-blue-dark);
  }

  .swagger-ui .scheme-container {
    background: rgba(255, 255, 255, 0.78);
    border: 1px solid var(--stimuli-border);
    box-shadow: 0 12px 40px rgba(26, 82, 118, 0.08);
    border-radius: 16px;
  }

  .swagger-ui .opblock.opblock-post {
    border-color: var(--stimuli-blue);
    background: rgba(26, 82, 118, 0.05);
  }

  .swagger-ui .opblock.opblock-post .opblock-summary-method {
    background: var(--stimuli-blue);
  }

  .swagger-ui .btn.authorize,
  .swagger-ui .btn.execute {
    background: var(--stimuli-blue);
    border-color: var(--stimuli-blue);
    color: #fff;
  }

  .swagger-ui .btn.authorize:hover,
  .swagger-ui .btn.execute:hover {
    background: var(--stimuli-blue-dark);
    border-color: var(--stimuli-blue-dark);
  }

  .swagger-ui .opblock,
  .swagger-ui .responses-inner,
  .swagger-ui .model-box {
    border-radius: 14px;
    box-shadow: 0 10px 30px rgba(17, 40, 56, 0.06);
  }

  .swagger-ui .markdown p code,
  .swagger-ui .markdown li code {
    background: rgba(26, 82, 118, 0.08);
    color: var(--stimuli-blue-dark);
    padding: 2px 6px;
    border-radius: 6px;
  }
</style>
""".strip()

app = FastAPI(
    title="stimul.li Micro-Learning Flash API",
    summary="AI-powered micro-learning and flashcard generation for commercial SaaS integrations.",
    description=API_DESCRIPTION,
    version="1.0.0",
    contact=CONTACT_INFO,
    terms_of_service="https://stimul.li/terms",
    docs_url=None,
    redoc_url=None,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.include_router(health_router)
app.include_router(billing_router)
app.include_router(export_router)
app.include_router(flash_router)
app.include_router(stimuli_router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        summary=app.summary,
        description=app.description,
        routes=app.routes,
        contact=CONTACT_INFO,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": LOGO_URL,
        "altText": "stimul.li",
        "backgroundColor": "#f5f1e8",
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    swagger_response = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} | API Docs",
        swagger_favicon_url=FAVICON_URL,
        swagger_ui_parameters={
            "defaultModelsExpandDepth": -1,
            "displayRequestDuration": True,
            "docExpansion": "none",
            "persistAuthorization": True,
            "syntaxHighlight.theme": "obsidian",
        },
    )
    html = swagger_response.body.decode("utf-8").replace("</head>", f"{SWAGGER_CUSTOM_CSS}</head>")
    return HTMLResponse(html, status_code=swagger_response.status_code)


@app.get("/reference", include_in_schema=False)
async def custom_redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} | Reference",
        redoc_favicon_url=FAVICON_URL,
    )


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    request.state.tenant_id = getattr(request.state, "tenant_id", "-")
    request.state.started_at = time.perf_counter()

    request_id_token = request_id_var.set(request_id)
    tenant_id_token = tenant_id_var.set(str(request.state.tenant_id))
    execution_time_token = execution_time_var.set(0.0)

    try:
        response = await call_next(request)
        execution_time = time.perf_counter() - request.state.started_at
        request.state.execution_time = execution_time
        execution_time_var.set(execution_time)
        tenant_id_var.set(str(getattr(request.state, "tenant_id", "-")))
        logger.info(
            "request completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
            },
        )
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        execution_time_var.reset(execution_time_token)
        tenant_id_var.reset(tenant_id_token)
        request_id_var.reset(request_id_token)


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    execution_time = time.perf_counter() - getattr(request.state, "started_at", time.perf_counter())
    execution_time_var.set(execution_time)
    tenant_id_var.set(str(getattr(request.state, "tenant_id", "-")))
    logger.exception(
        "database error during request",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": 500,
        },
        exc_info=exc,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error."},
        headers={"X-Request-ID": request.state.request_id},
    )


@app.exception_handler(AIServiceTimeoutError)
@app.exception_handler(APITimeoutError)
async def ai_timeout_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    execution_time = time.perf_counter() - getattr(request.state, "started_at", time.perf_counter())
    execution_time_var.set(execution_time)
    tenant_id_var.set(str(getattr(request.state, "tenant_id", "-")))
    logger.exception(
        "ai timeout during request",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": 500,
        },
        exc_info=exc,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error."},
        headers={"X-Request-ID": request.state.request_id},
    )


@app.get("/", tags=["root"])
def read_root() -> dict[str, str]:
    return {"message": "Hello World"}


@app.get("/me", tags=["auth"])
def read_current_user(current_user: User = Depends(get_current_user)) -> dict[str, str]:
    return {
        "email": current_user.email,
        "api_key_prefix": current_user.api_key[:5],
    }
