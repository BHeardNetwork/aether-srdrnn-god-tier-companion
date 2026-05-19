 """
SRDRNN PyTorch Models
Sparse Recall Deep Reconstruction Neural Network components.
Production-grade, modular, typed.
"""

import torch
import torch.nn as nn
from typing import Optional, Tuple


class SparseEncoder(nn.Module):
    """Encodes input to sparse latent representation."""
    def __init__(self, input_dim: int, hidden_dim: int, sparsity_level: float = 0.05):
        super().__init__()
        self.fc = nn.Linear(input_dim, hidden_dim)
        self.relu = nn.ReLU()
        self.sparsity_level = sparsity_level  # target fraction active

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = self.relu(self.fc(x))
        # Simple top-k sparsity (can be replaced with more advanced)
        k = max(1, int(self.sparsity_level * h.shape[-1]))
        topk_values, topk_indices = torch.topk(h, k, dim=-1)
        sparse_h = torch.zeros_like(h)
        sparse_h.scatter_(-1, topk_indices, topk_values)
        return sparse_h


class DeepReconstructor(nn.Module):
    """Deep network that reconstructs rich output from sparse cues."""
    def __init__(self, latent_dim: int, output_dim: int, hidden_dim: int = 512, num_layers: int = 4):
        super().__init__()
        layers = []
        layers.append(nn.Linear(latent_dim, hidden_dim))
        layers.append(nn.ReLU())
        for _ in range(num_layers - 2):
            layers.append(nn.Linear(hidden_dim, hidden_dim))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(0.1))
        layers.append(nn.Linear(hidden_dim, output_dim))
        self.net = nn.Sequential(*layers)

    def forward(self, z_sparse: torch.Tensor) -> torch.Tensor:
        return self.net(z_sparse)


class IterativeRefiner(nn.Module):
    """Optional iterative deep reconstructor (like unfolded networks or diffusion step)."""
    def __init__(self, dim: int, num_iterations: int = 3):
        super().__init__()
        self.num_iterations = num_iterations
        self.refine = nn.Sequential(
            nn.Linear(dim, dim),
            nn.ReLU(),
            nn.Linear(dim, dim)
        )

    def forward(self, z: torch.Tensor) -> torch.Tensor:
        for _ in range(self.num_iterations):
            z = z + self.refine(z)  # residual refinement
        return z


class SRDRNN(nn.Module):
    """
    Full Sparse Recall Deep Reconstruction Neural Network module.
    Combines sparse encoding, recall logic (external), and deep reconstruction.
    Can be used standalone or integrated with memory systems.
    """
    def __init__(
        self,
        input_dim: int = 768,      # e.g. embedding dim
        latent_dim: int = 2048,
        output_dim: int = 768,
        sparsity: float = 0.03,
        use_iterative: bool = True
    ):
        super().__init__()
        self.encoder = SparseEncoder(input_dim, latent_dim, sparsity)
        self.reconstructor = DeepReconstructor(latent_dim, output_dim)
        self.iterative_refiner = IterativeRefiner(output_dim) if use_iterative else None
        self.latent_dim = latent_dim

    def forward(self, x: torch.Tensor, recalled_sparse: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        x: input cue/embedding
        recalled_sparse: optional pre-recalled sparse vector from memory
        """
        if recalled_sparse is None:
            z_sparse = self.encoder(x)
        else:
            z_sparse = recalled_sparse

        reconstruction = self.reconstructor(z_sparse)

        if self.iterative_refiner is not None:
            reconstruction = self.iterative_refiner(reconstruction)

        return reconstruction

    def get_sparse_code(self, x: torch.Tensor) -> torch.Tensor:
        return self.encoder(x)

    def reconstruct_from_sparse(self, z_sparse: torch.Tensor) -> torch.Tensor:
        rec = self.reconstructor(z_sparse)
        if self.iterative_refiner:
            rec = self.iterative_refiner(rec)
        return rec