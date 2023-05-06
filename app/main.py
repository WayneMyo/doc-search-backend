import logging

from app.app import app
from app.logging_config import setup_logging
from app.routes.documents import router as documents_router

"""
The main FastAPI application file, containing:
1. documents_router: The router for the documents API endpoints.
"""

setup_logging()
logger = logging.getLogger(__name__)
app.include_router(documents_router)  # Include the documents router in the main app