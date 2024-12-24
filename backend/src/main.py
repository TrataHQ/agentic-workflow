from typing import Any, Dict, Optional
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from backend.src.api.routes import app as app_router
from backend.src.utils.auth import AuthProvider, NoAuthProvider
import uvicorn

def create_app(
    auth_provider: Optional[AuthProvider] = None,
    title: str = "Agentic AI Workflow Management System",
    description: str = "Workflow Management System for Agentic AI",
    version: str = "1.0.0",
    **kwargs
) -> FastAPI:
    """
    Factory function to create the FastAPI application.
    Can be used either as a standalone app or as a library component.
    
    Args:
        auth_provider: Custom authentication provider. If None, uses NoAuthProvider
        title: API title
        description: API description
        version: API version
        **kwargs: Additional FastAPI configuration parameters
    """
    app = FastAPI(
        openapi_url="/api/openapi.json",
        docs_url=None,
        title=title,
        description=description,
        version=version,
        servers=[
            {"url": "http://localhost:8001", "description": "Localhost"},
        ],
        **kwargs
    )

    # CORS middleware configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Set up auth provider
    app.state.auth_provider = auth_provider or NoAuthProvider()
    app.include_router(app_router.router)

    @app.get('/workflows/status',
            tags=['Health'],
            summary="Heart Beat Status Of Workflow Service",
            description="Heart Beat check to check the health of Workflow Service",
            responses={
                200: {
                    "description": "Workflow Service is healthy",
                    "content": {
                        "application/json": {
                            "examples": [{"default": {"status": "HEALTHY"}}]
                        }
                    }
                }
            }
    )
    async def status() -> Dict[str, Any]:
        return {"status": "HEALTHY"}

    return app

# For standalone usage
app = create_app()

def run_dev():
    uvicorn.run("backend.src.main:app", host='0.0.0.0', port=8001, reload=True)

def run():
    uvicorn.run("backend.src.main:app", host='0.0.0.0', port=8001, reload=False)
