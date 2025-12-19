"""Thread-safe API Key Rotator for load balancing across multiple keys.

This module provides a round-robin key rotation mechanism to distribute
API requests across multiple keys, helping to avoid rate limits.

Usage:
    from app.shared.integrations.key_rotator import megallm_key_rotator
    
    api_key = megallm_key_rotator.get_next_key()
"""

import logging
import os
import threading
from typing import List

from dotenv import load_dotenv

# Ensure .env is loaded before accessing os.environ
load_dotenv()

logger = logging.getLogger(__name__)


class KeyRotator:
    """Thread-safe round-robin API key rotator.
    
    Distributes API calls across multiple keys to avoid per-key rate limits.
    Each call to get_next_key() returns the next key in rotation.
    
    Attributes:
        _keys: List of API keys to rotate through
        _index: Current position in rotation
        _lock: Thread lock for safe concurrent access
    """
    
    def __init__(self, keys: List[str], name: str = "default"):
        """Initialize the key rotator.
        
        Args:
            keys: List of API keys (must have at least one)
            name: Name for logging identification
            
        Raises:
            ValueError: If keys list is empty
        """
        if not keys:
            raise ValueError("At least one API key is required")
        
        self._keys = keys
        self._name = name
        self._index = 0
        self._lock = threading.Lock()
        self._request_count = 0
        
        logger.info(f"[KeyRotator:{name}] Initialized with {len(keys)} API keys")
    
    def get_next_key(self) -> str:
        """Get next API key in rotation (thread-safe).
        
        Returns:
            The next API key in round-robin order
        """
        with self._lock:
            key = self._keys[self._index]
            key_index = self._index + 1  # 1-based for logging
            self._index = (self._index + 1) % len(self._keys)
            self._request_count += 1
            
            # Log rotation (mask key for security, only show last 8 chars)
            masked_key = f"...{key[-8:]}" if len(key) > 8 else key
            logger.info(
                f"[KeyRotator:{self._name}] Request #{self._request_count} "
                f"using key {key_index}/{len(self._keys)} ({masked_key})"
            )
            
            return key
    
    @property
    def total_keys(self) -> int:
        """Number of keys in rotation."""
        return len(self._keys)
    
    @property
    def request_count(self) -> int:
        """Total number of requests made through this rotator."""
        return self._request_count
    
    def get_stats(self) -> dict:
        """Get rotation statistics for debugging."""
        return {
            "name": self._name,
            "total_keys": len(self._keys),
            "current_index": self._index,
            "total_requests": self._request_count,
        }


def load_megallm_keys() -> List[str]:
    """Load all MEGALLM_API_KEY_* from environment variables.
    
    Looks for keys in format: MEGALLM_API_KEY_1, MEGALLM_API_KEY_2, etc.
    Falls back to single MEGALLM_API_KEY for backward compatibility.
    
    Returns:
        List of API keys found in environment
    """
    keys = []
    i = 1
    
    # Load numbered keys (MEGALLM_API_KEY_1, MEGALLM_API_KEY_2, ...)
    while True:
        key = os.environ.get(f"MEGALLM_API_KEY_{i}")
        if not key:
            break
        keys.append(key)
        i += 1
    
    # Fallback to single key for backward compatibility
    if not keys:
        single_key = os.environ.get("MEGALLM_API_KEY")
        if single_key:
            keys = [single_key]
            logger.warning(
                "[KeyRotator] Using legacy MEGALLM_API_KEY. "
                "Consider migrating to MEGALLM_API_KEY_1, MEGALLM_API_KEY_2, etc."
            )
    
    if keys:
        logger.info(f"[KeyRotator] Loaded {len(keys)} MegaLLM API key(s)")
    else:
        logger.warning("[KeyRotator] No MegaLLM API keys found in environment")
    
    return keys


# Singleton instance for MegaLLM key rotation
_megallm_keys = load_megallm_keys()
megallm_key_rotator: KeyRotator | None = None

if _megallm_keys:
    megallm_key_rotator = KeyRotator(_megallm_keys, name="MegaLLM")
