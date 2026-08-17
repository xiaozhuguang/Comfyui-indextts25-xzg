#!/usr/bin/env python3
"""Convenience wrapper to download the official IndexTTS 2.5 model.

Usage (run with your ComfyUI's Python):

    python scripts/download_models.py --source modelscope --accept-license
    python scripts/download_models.py --source huggingface --accept-license
"""

from __future__ import annotations

import sys
from pathlib import Path


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    try:
        from services.downloader import main
    except ImportError:
        from services.downloader import main
    raise SystemExit(main())
