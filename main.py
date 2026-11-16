import sys
from pathlib import Path

# Ensure backend directory is in python module search path
root_dir = Path(__file__).resolve().parent
backend_dir = root_dir / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Import the actual FastAPI app from backend/app/main.py
from app.main import app
