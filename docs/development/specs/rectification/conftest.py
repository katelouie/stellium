"""Put this standalone toolkit's dir on sys.path so tests use flat imports
(`from models import ...`), matching how the scripts run themselves.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
