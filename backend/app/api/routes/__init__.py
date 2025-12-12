# API Routes Package
# 
# This package contains route modules for different API sections.
# The main API routes are imported from the parent routes.py file to maintain
# backward compatibility.

import importlib.util
from pathlib import Path

# Import router from the sibling routes.py file
try:
    _routes_file = Path(__file__).parent.parent / "routes.py"
    if not _routes_file.exists():
        raise FileNotFoundError(f"Routes file not found: {_routes_file}")
    
    _spec = importlib.util.spec_from_file_location("_routes_main", _routes_file)
    if _spec is None or _spec.loader is None:
        raise ImportError(f"Failed to create module spec for {_routes_file}")
    
    _routes_main = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_routes_main)
    
    # Export router for backward compatibility
    router = _routes_main.router
except Exception as e:
    # If dynamic import fails, raise a clear error
    raise ImportError(
        f"Failed to import router from routes.py: {e}. "
        "Please ensure app/api/routes.py exists and is valid."
    ) from e

# Make all exports from routes.py available
__all__ = ['router']

