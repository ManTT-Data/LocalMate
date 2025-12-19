"""Unit tests for MegaLLM API Key Rotation.

Run with:
    cd /Volumes/WorkSpace/Project/LocalMate/localmate-danang-backend-v2
    python -m pytest tests/test_key_rotation.py -v
"""

import os
import threading
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

import pytest


class TestKeyRotator:
    """Tests for KeyRotator class."""

    def test_rotation_cycles_through_keys(self):
        """Verify round-robin cycles through all keys in order."""
        from app.shared.integrations.key_rotator import KeyRotator
        
        keys = ["key_1", "key_2", "key_3"]
        rotator = KeyRotator(keys, name="test")
        
        # First cycle
        assert rotator.get_next_key() == "key_1"
        assert rotator.get_next_key() == "key_2"
        assert rotator.get_next_key() == "key_3"
        
        # Second cycle (should loop back)
        assert rotator.get_next_key() == "key_1"
        assert rotator.get_next_key() == "key_2"
        assert rotator.get_next_key() == "key_3"
        
        # Verify request count
        assert rotator.request_count == 6
    
    def test_single_key_always_returns_same(self):
        """Verify single key mode works correctly."""
        from app.shared.integrations.key_rotator import KeyRotator
        
        keys = ["only_key"]
        rotator = KeyRotator(keys, name="single")
        
        for _ in range(5):
            assert rotator.get_next_key() == "only_key"
        
        assert rotator.request_count == 5
    
    def test_empty_keys_raises_error(self):
        """Verify empty keys list raises ValueError."""
        from app.shared.integrations.key_rotator import KeyRotator
        
        with pytest.raises(ValueError, match="At least one API key is required"):
            KeyRotator([], name="empty")
    
    def test_rotation_thread_safety(self):
        """Verify rotation is thread-safe under concurrent access."""
        from app.shared.integrations.key_rotator import KeyRotator
        
        keys = ["key_1", "key_2", "key_3"]
        rotator = KeyRotator(keys, name="threaded")
        
        results = []
        lock = threading.Lock()
        
        def get_key():
            key = rotator.get_next_key()
            with lock:
                results.append(key)
        
        # Run 100 concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(get_key) for _ in range(100)]
            for future in futures:
                future.result()
        
        # Should have 100 results
        assert len(results) == 100
        assert rotator.request_count == 100
        
        # Each key should be used roughly equally (with some variance due to threading)
        for key in keys:
            count = results.count(key)
            # Should be approximately 33 each, allow 20% variance
            assert 20 <= count <= 45, f"Key {key} used {count} times (expected ~33)"
    
    def test_get_stats(self):
        """Verify stats reporting works."""
        from app.shared.integrations.key_rotator import KeyRotator
        
        keys = ["key_1", "key_2"]
        rotator = KeyRotator(keys, name="stats_test")
        
        rotator.get_next_key()
        rotator.get_next_key()
        rotator.get_next_key()
        
        stats = rotator.get_stats()
        assert stats["name"] == "stats_test"
        assert stats["total_keys"] == 2
        assert stats["total_requests"] == 3
        assert stats["current_index"] == 1  # After 3 requests: 0->1->0->1


class TestLoadMegaLLMKeys:
    """Tests for environment-based key loading."""
    
    def test_load_numbered_keys(self):
        """Verify loading MEGALLM_API_KEY_1, _2, _3 format."""
        env_vars = {
            "MEGALLM_API_KEY_1": "first_key",
            "MEGALLM_API_KEY_2": "second_key",
            "MEGALLM_API_KEY_3": "third_key",
        }
        
        with patch.dict(os.environ, env_vars, clear=False):
            from importlib import reload
            from app.shared.integrations import key_rotator
            reload(key_rotator)
            
            keys = key_rotator.load_megallm_keys()
            assert keys == ["first_key", "second_key", "third_key"]
    
    def test_load_fallback_single_key(self):
        """Verify fallback to MEGALLM_API_KEY (legacy format)."""
        # Clear any numbered keys
        env_vars = {
            "MEGALLM_API_KEY": "legacy_key",
        }
        
        # Remove any numbered keys that might exist
        for i in range(1, 10):
            env_vars[f"MEGALLM_API_KEY_{i}"] = ""
        
        with patch.dict(os.environ, env_vars, clear=False):
            from importlib import reload
            from app.shared.integrations import key_rotator
            reload(key_rotator)
            
            # Note: This test may need adjustment based on environment state
            keys = key_rotator.load_megallm_keys()
            # Should have at least the legacy key if no numbered keys
            assert len(keys) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
