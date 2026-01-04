"""SUKP instance data model and I/O operations."""

import json
from dataclasses import dataclass, asdict
from typing import List


@dataclass
class SUKPInstance:
    """Represents a Set Union Knapsack Problem instance.
    
    Attributes:
        m: Number of elements
        n: Number of sets
        weights: List of element weights (length m)
        profits: List of set profits (length n)
        sets: List of sets, where sets[i] contains indices of elements in set i
        capacity: Knapsack capacity C
        density: Density of the instance (used for generation)
        cap_ratio: Capacity ratio (used for generation)
        seed: Random seed used for generation
    """
    m: int
    n: int
    weights: List[float]
    profits: List[float]
    sets: List[List[int]]
    capacity: float
    density: float
    cap_ratio: float
    seed: int
    
    def to_dict(self) -> dict:
        """Convert instance to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SUKPInstance':
        """Create instance from dictionary."""
        return cls(**data)
    
    def save(self, filepath: str) -> None:
        """Save instance to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, filepath: str) -> 'SUKPInstance':
        """Load instance from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)
    
    def __str__(self) -> str:
        return (f"SUKPInstance(m={self.m}, n={self.n}, "
                f"density={self.density}, cap_ratio={self.cap_ratio}, "
                f"capacity={self.capacity:.2f}, seed={self.seed})")

