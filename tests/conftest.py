"""Pytest config: add src to path so mcp_template is importable without pip install -e ."""
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
_src = _root / "src"
if _src.exists() and str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

# Load .env so tests see env-based credentials when present (e.g. for backend integration tests).
try:
    from dotenv import load_dotenv
    load_dotenv(_root / ".env")
except ImportError:
    pass
