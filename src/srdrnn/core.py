 """
SRDRNN Core Orchestrator
Production-grade integration of Sparse Recall + Deep Reconstruction.
"""

from __future__ import annotations
import torch
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel
import numpy as np

from .models import SRDRNN as SRDRNNModel


class MemoryItem(BaseModel):
    id: str
    content: str
    embedding: List[float]
    importance: float = 1.0
    timestamp: str
    tags: List[str] = []
    consolidated: bool = False


class SRDRNNCore:
    """
    High-level SRDRNN system.
    - Manages PyTorch model
    - Interfaces with hybrid memory for sparse recall
    - Performs deep reconstruction
    - Exposes methods for chat grounding, memory ingestion, and REM
    """
    def __init__(
        self,
        embedding_dim: int = 768,
        latent_dim: int = 2048,
        device: str = "cpu"
    ):
        self.device = torch.device(device)
        self.model = SRDRNNModel(
            input_dim=embedding_dim,
            latent_dim=latent_dim,
            output_dim=embedding_dim
        ).to(self.device)
        self.model.eval()

        # In production: replace with real embedder (local sentence-transformers or LLM hidden states)
        self.embedding_dim = embedding_dim

    def embed(self, text: str) -> np.ndarray:
        """Placeholder embedding. Replace with real local embedder."""
        np.random.seed(hash(text) % (2**32))
        return np.random.randn(self.embedding_dim).astype(np.float32)

    def sparse_recall(
        self,
        query_embedding: np.ndarray,
        memory_items: List[MemoryItem],
        top_k: int = 5,
        sparsity: float = 0.03
    ) -> Tuple[List[MemoryItem], torch.Tensor]:
        """
        Perform sparse recall from memory store.
        Returns top relevant items + aggregated sparse vector.
        """
        if not memory_items:
            return [], torch.zeros(self.model.latent_dim)

        # Simple similarity for scaffold (cosine). In prod: use vector DB + graph spreading
        query_t = torch.tensor(query_embedding, dtype=torch.float32)
        sims = []
        for item in memory_items:
            item_t = torch.tensor(item.embedding, dtype=torch.float32)
            sim = torch.nn.functional.cosine_similarity(query_t.unsqueeze(0), item_t.unsqueeze(0))
            sims.append((sim.item(), item))

        sims.sort(key=lambda x: x[0], reverse=True)
        top_items = [item for _, item in sims[:top_k]]

        # Create sparse aggregated vector (demo)
        if top_items:
            embs = torch.stack([torch.tensor(it.embedding) for it in top_items])
            agg = embs.mean(dim=0)
            # Apply simple sparsity
            k = max(1, int(sparsity * agg.shape[0]))
            topk_val, topk_idx = torch.topk(agg, k)
            sparse_vec = torch.zeros_like(agg)
            sparse_vec[topk_idx] = topk_val
        else:
            sparse_vec = torch.zeros(self.model.latent_dim)

        return top_items, sparse_vec.to(self.device)

    def deep_reconstruct(
        self,
        sparse_vector: torch.Tensor,
        context: Optional[str] = None
    ) -> torch.Tensor:
        """Deep reconstruction from sparse recall vector."""
        with torch.no_grad():
            rec = self.model.reconstruct_from_sparse(sparse_vector)
        return rec

    def process_query(
        self,
        query: str,
        memory_items: List[MemoryItem]
    ) -> Dict[str, Any]:
        """
        Full SRDRNN pipeline for a query:
        1. Embed query
        2. Sparse recall relevant memories
        3. Deep reconstruct enriched representation
        4. Return grounded context for LLM
        """
        q_emb = self.embed(query)
        recalled_items, sparse_vec = self.sparse_recall(q_emb, memory_items)

        reconstructed = self.deep_reconstruct(sparse_vec)

        # In real system: feed reconstructed + recalled content to LLM prompt
        context_text = "\n".join([item.content for item in recalled_items]) if recalled_items else "No strong memories recalled."

        return {
            "recalled_items": [item.model_dump() for item in recalled_items],
            "reconstructed_vector": reconstructed.cpu().numpy().tolist(),
            "context_for_llm": f"Relevant memories (sparse recall + deep recon):\n{context_text}",
            "sparsity_used": True
        }

    def ingest_memory(self, content: str, importance: float = 1.0) -> MemoryItem:
        """Create and return a new memory item (caller persists it)."""
        emb = self.embed(content)
        import uuid
        from datetime import datetime
        return MemoryItem(
            id=str(uuid.uuid4()),
            content=content,
            embedding=emb.tolist(),
            importance=importance,
            timestamp=datetime.utcnow().isoformat()
        )