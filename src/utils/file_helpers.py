"""File I/O and path utilities."""
import json
from pathlib import Path
from typing import Any
import aiofiles
from src.core.logging import get_logger

logger = get_logger("file_helpers")


async def write_json_async(path: Path, data: Any) -> None:
    """Write JSON data to file asynchronously."""
    try:
        async with aiofiles.open(path, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(data, ensure_ascii=False, indent=2))
        logger.info(f"Wrote JSON to {path}")
    except Exception as e:
        logger.error(f"Failed to write JSON to {path}: {e}")
        raise


async def read_json_async(path: Path) -> Any:
    """Read JSON data from file asynchronously."""
    try:
        async with aiofiles.open(path, 'r', encoding='utf-8') as f:
            content = await f.read()
        return json.loads(content)
    except Exception as e:
        logger.error(f"Failed to read JSON from {path}: {e}")
        raise


def write_json_sync(path: Path, data: Any) -> None:
    """Write JSON data to file synchronously."""
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Wrote JSON to {path}")
    except Exception as e:
        logger.error(f"Failed to write JSON to {path}: {e}")
        raise


def read_json_sync(path: Path) -> Any:
    """Read JSON data from file synchronously."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to read JSON from {path}: {e}")
        raise
