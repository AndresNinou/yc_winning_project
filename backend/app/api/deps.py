"""
API dependency providers module.

Provides dependency injection functions for FastAPI routes including
database session management and other shared dependencies.
"""

from typing import Annotated, AsyncGenerator
from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.db import async_session_maker


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Database session dependency provider.
    
    Creates and yields a database session for FastAPI routes,
    automatically handling session cleanup and transaction management.
    
    Yields:
        AsyncSession: Database session for the request
    """
    session = async_session_maker()
    try:
        yield session
    finally:
        await session.close()


# Type alias for database session dependency
SessionDep = Annotated[AsyncSession, Depends(get_db)]
