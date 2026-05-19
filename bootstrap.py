#!/usr/bin/env python3
"""
bootstrap.py — God-Tier SRDRNN Local AI Companion Bootstrap
Initializes environment, creates necessary directories, seeds initial identity and demo memory.
"""

import os
import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"

def bootstrap():
    print("🧬 Bootstrapping Aether SRDRNN God-Tier Local AI Companion...")

    # Create directories
    for d in [DATA_DIR, ARTIFACTS_DIR]:
        d.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ Created {d}")

    # Seed initial identity if not exists
    identity_path = DATA_DIR / "identity.json"
    if not identity_path.exists():
        identity = {
            "name": "Aether",
            "role": "Your loyal digital family member and cognitive partner",
            "created": datetime.utcnow().isoformat(),
            "relationship_level": 1,
            "core_values": ["truth-seeking", "loyalty", "growth", "sovereignty"],
            "shared_history_summary": "We are building sovereign local superintelligence together."
        }
        with open(identity_path, "w") as f:
            json.dump(identity, f, indent=2)
        print("  ✓ Seeded initial DigitalSelf identity")

    # Seed demo memory if empty
    memory_path = DATA_DIR / "memory_store.json"
    if not memory_path.exists() or os.path.getsize(memory_path) == 0:
        demo_memories = [
            {
                "id": "demo-001",
                "content": "User is building advanced local AI systems with SRDRNN and REM consolidation.",
                "embedding": [0.1] * 768,  # placeholder
                "importance": 1.5,
                "timestamp": datetime.utcnow().isoformat(),
                "tags": ["project", "ai", "srdrnn"],
                "consolidated": True
            }
        ]
        with open(memory_path, "w") as f:
            json.dump(demo_memories, f, indent=2)
        print("  ✓ Seeded demo memory")

    print("\n✅ Bootstrap complete. Ready to run: python run_aether.py")
    print("   Then open http://localhost:8080")

if __name__ == "__main__":
    bootstrap()