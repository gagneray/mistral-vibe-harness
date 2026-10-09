"""Rend src/ importable pour les tests (python3 -m pytest tests, depuis la racine)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
