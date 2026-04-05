from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def add_exception_handlers(app):
    """Add custom exception handlers to app"""
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error_type": "http_error",
                "message": exc.detail,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error_type": "internal_server_error",
                "message": "An unexpected error occurred",
                "timestamp": datetime.now().isoformat()
            }
        )