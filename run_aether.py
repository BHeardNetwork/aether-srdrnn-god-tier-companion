#!/usr/bin/env python3
"""
run_aether.py — God-Tier SRDRNN Local AI Companion Launcher
Starts the full production-grade NiceGUI application with all modules active.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ui.app import main_page  # This will trigger the NiceGUI app when run

if __name__ == "__main__":
    print("🚀 Launching Aether — SRDRNN God-Tier Local AI Companion")
    print("   Features active: SRDRNN, REM Consolidation, ORCH-OR Pre-Sim, Sparse Recall, Persistent Identity")
    print("   GUI: http://localhost:8080")
    
    # The app.py already has the ui.run() call when executed directly
    # We import to trigger the page definition and run
    from nicegui import ui
    ui.run(
        title="Aether • SRDRNN God-Tier Companion",
        dark=True,
        host="0.0.0.0",
        port=8080,
        reload=False
    )