"""
Helper utilities

Các hàm helper nhỏ dùng chung
"""

from typing import Any, Dict, Optional
import re


def normalize_text(text: str) -> str:
    """
    Normalize text by removing extra whitespace and converting to lowercase
    
    Args:
        text: Input text
        
    Returns:
        Normalized text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    # Convert to lowercase
    return text.lower()


def safe_dict(obj: Any, *keys: str, default: Any = None) -> Any:
    """
    Safely get nested dictionary value
    
    Args:
        obj: Dictionary or object
        *keys: Keys to traverse
        default: Default value if key not found
        
    Returns:
        Value at key path or default
        
    Example:
        safe_dict({"a": {"b": 1}}, "a", "b") -> 1
        safe_dict({"a": {}}, "a", "b", default=0) -> 0
    """
    result = obj
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key)
        else:
            try:
                result = getattr(result, key)
            except AttributeError:
                return default
        
        if result is None:
            return default
    
    return result


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate a string to a maximum length
    
    Args:
        text: Input text
        max_length: Maximum length
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple dictionaries
    
    Args:
        *dicts: Dictionaries to merge
        
    Returns:
        Merged dictionary
    """
    result: Dict[str, Any] = {}
    for d in dicts:
        result.update(d)
    return result
