# API Routes Package
# 
# This package contains route modules for different API sections.
# The main API routes are imported from the parent routes.py file to maintain
# backward compatibility.

import sys
import importlib.util
from pathlib import Path

# Import router from the sibling routes.py file
_routes_file = Path(__file__).parent.parent / "routes.py"
_spec = importlib.util.spec_from_file_location("_routes_main", _routes_file)
_routes_main = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_routes_main)

# Export router for backward compatibility
router = _routes_main.router

# Make all exports from routes.py available
__all__ = ['router']

