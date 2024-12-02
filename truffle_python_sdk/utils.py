from functools import wraps
from typing import Literal

import stringcase
from pydantic import BaseModel


def tool(name: str = None):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return func(self, *args, **kwargs)
        
        tool_args = {
            "name": name or func.__name__
        }
        
        wrapper.__truffle_tool__ = tool_args
        
        return wrapper
    return decorator

