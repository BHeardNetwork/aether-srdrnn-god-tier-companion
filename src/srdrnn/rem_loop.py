 """
REM Consolidation Loop
Biological sleep-inspired memory consolidation for SRDRNN systems.
- Sparse replay
- Deep reconstruction & abstraction
- Semantic graph update
- Pruning for sparsity
- Creative recombination (optional)
"""

import asyncio
from typing import List, Dict, Any
from datetime import datetime
import logging

from .core import SRDRNNCore, MemoryItem

logger = logging.getLogger("REM_Loop")


class REMConsolidationLoop:
    def __init__(self, srdrnn_core: SRDRNNCore, memory_store: Any):
        self.core = srdrnn_core
        self.memory_store = memory_store  # In prod: graph DB or hybrid store
        self.is_running = False
        self.last_run = None
        self.stats = {"cycles_run": 0, "memories_consolidated": 0, "pruned": 0}

    async def run_consolidation_cycle(self, unconsolidated_memories: List[MemoryItem]) -> Dict[str, Any]:
        """One full REM-like consolidation cycle."""
        if not unconsolidated_memories:
            return {"status": "no_memories", "processed": 0}

        logger.info(f"REM Cycle starting with {len(unconsolidated_memories)} memories...")

        consolidated_count = 0
        pruned_count = 0

        for mem in unconsolidated_memories:
            # 1. Sparse replay (use the memory's own embedding as cue)
            recalled, sparse_vec = self.core.sparse_recall(
                np.array(mem.embedding), 
                unconsolidated_memories + self._get_all_memories(),  # simplified
                top_k=3
           
 )

            # 2. Deep reconstruction
            reconstructed = self.core.deep_reconstruct(sparse_vec)

            # 3. Abstraction & semantic update (demo: mark as consolidated + boost importance)
            mem.consolidated = True
            mem.importance = min(2.0, mem.importance * 1.15)  # reinforce

            # In real system:
            # - Cluster similar memories
            # - Create/update semantic nodes in graph
            # - Weave into episodic narrative
            # - Update edges in semantic-episodic graph

            consolidated_count += 1

            # 4. Pruning example (low importance after consolidation)
            if mem.importance < 0.3:
                # Would remove or archive in real store
                pruned_count += 1

        self.stats["cycles_run"] += 1
        self.stats["memories_consolidated"] += consolidated_count
        self.stats["pruned"] += pruned_count
        self.last_run = datetime.utcnow().isoformat()

        logger.info(f"REM Cycle complete. Consolidated: {consolidated_count}, Pruned: {pruned_count}")

        return {
            "status": "success",
            "processed": len(unconsolidated_memories),
            "consolidated": consolidated_count,
            "pruned": pruned_count,
            "stats": self.stats,
            "timestamp": self.last_run
        }

    def _get_all_memories(self) -> List[MemoryItem]:
        # Placeholder - in real impl query the store
        return []

    async def start_background_loop(self, interval_seconds: int = 3600):
        """Run REM periodically (e.g., every hour or on idle)."""
        self.is_running = True
        while self.is_running:
            # In real app: fetch unconsolidated from persistent store
            # For demo, this is manual trigger mostly
            await asyncio.sleep(interval_seconds)
            # Auto-trigger logic here if desired

    def stop(self):
        self.is_running = False