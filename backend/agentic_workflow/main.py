from typing import Any, Dict, Optional
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from agentic_workflow.api.routes.app import router as app_router
from agentic_workflow.api.routes.connection import router as connection_router
from agentic_workflow.api.routes.workflow import router as workflow_router
from agentic_workflow.utils.auth import AuthProvider
from tests.no_auth_provider import NoAuthProvider
import uvicorn
from agentic_workflow.utils import logger

def create_app(
    auth_provider: Optional[AuthProvider] = None,
    title: str = "Agentic AI Workflow Management System",
    description: str = "Workflow Management System for Agentic AI",
    version: str = "1.0.0",
    **kwargs
) -> FastAPI:
    
    logger.log_setup()
    
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
        docs_url="/api/docs",
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
    app.state.auth_provider = auth_provider
    app.include_router(app_router)
    app.include_router(connection_router)
    app.include_router(workflow_router)
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

def run_dev():
    app = create_app(auth_provider=NoAuthProvider())
    uvicorn.run(app, host='0.0.0.0', port=8001, reload=True)

def run():
    app = create_app(auth_provider=NoAuthProvider())
    uvicorn.run(app, host='0.0.0.0', port=8001, reload=False)
