"""REST wrapper for KP registry SQLite server."""
from collections import defaultdict
import sqlite3
from typing import Dict, List

import aiosqlite
from fastapi import Body, Depends, HTTPException, APIRouter, status

from ..models import KP
from ..config import settings
from ..registry import Registry

router = APIRouter()


async def get_registry():
    """Get KP registry."""
    async with Registry(settings.db_uri) as registry:
        yield registry


example = {
    'my_kp': {
        'url': 'http://my_kp_url',
        'operations': [{
            'source_type': 'disease',
            'edge_type': 'related to',
            'target_type': 'gene',
        }],
    }
}


@router.get('/kps')
async def get_all_knowledge_providers(
        registry=Depends(get_registry),
):
    """Get all knowledge providers."""
    return await registry.get_all()


@router.get('/kps/{uid}')
async def get_knowledge_provider(
        uid: str,
        registry=Depends(get_registry),
):
    """Get a knowledge provider by url."""
    return await registry.get_one(uid)


@router.post('/kps', status_code=status.HTTP_201_CREATED)
async def add_knowledge_provider(
        kps: Dict[str, KP] = Body(..., example=example),
        registry=Depends(get_registry),
):
    """Add a knowledge provider."""
    kps = {key: value.dict() for key, value in kps.items()}
    await registry.add(**kps)


@router.delete('/kps/{uid}', status_code=status.HTTP_204_NO_CONTENT)
async def remove_knowledge_provider(
        uid: str,
        registry=Depends(get_registry),
):
    """Delete a knowledge provider."""
    await registry.delete_one(uid)


@router.post('/search')
async def search_for_knowledge_providers(
        source_type: List[str] = Body(..., example=['drug']),
        edge_type: List[str] = Body(..., example=['-related_to->']),
        target_type: List[str] = Body(..., example=['named_thing']),
        registry=Depends(get_registry),
):
    """Search for knowledge providers matching a specification."""
    return await registry.search(source_type, edge_type, target_type)


@router.post('/clear', status_code=status.HTTP_204_NO_CONTENT)
async def clear_kps(
    registry=Depends(get_registry),
):
    """Clear all registered KPs."""
    await registry.delete_all()
