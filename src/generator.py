"""Generate synthetic SUKP instances."""

import random
from typing import List
from .sukp_instance import SUKPInstance


def generate_sukp_instance(
    m: int,
    n: int,
    density: float,
    cap_ratio: float,
    seed: int,
    weight_range: tuple = (1.0, 100.0),
    profit_range: tuple = (1.0, 100.0)
) -> SUKPInstance:
    """Generate a synthetic SUKP instance.
    
    Args:
        m: Number of elements
        n: Number of sets
        density: Probability that an element belongs to a set (0.0 to 1.0)
        cap_ratio: Capacity ratio (capacity = cap_ratio * sum(all_weights))
        seed: Random seed for reproducibility
        weight_range: (min, max) range for element weights
        profit_range: (min, max) range for set profits
    
    Returns:
        A SUKPInstance object
    """
    random.seed(seed)
    
    # Generate element weights
    weights = [
        random.uniform(weight_range[0], weight_range[1])
        for _ in range(m)
    ]
    
    # Generate set profits
    profits = [
        random.uniform(profit_range[0], profit_range[1])
        for _ in range(n)
    ]
    
    # Generate sets: each element j belongs to set i with probability density
    sets: List[List[int]] = [[] for _ in range(n)]
    for i in range(n):
        for j in range(m):
            if random.random() < density:
                sets[i].append(j)
    
    # Calculate capacity
    total_weight = sum(weights)
    capacity = cap_ratio * total_weight
    
    return SUKPInstance(
        m=m,
        n=n,
        weights=weights,
        profits=profits,
        sets=sets,
        capacity=capacity,
        density=density,
        cap_ratio=cap_ratio,
        seed=seed
    )


def generate_all_instances(base_seed: int = 42) -> List[SUKPInstance]:
    """Generate all 12 instances for experiments.
    
    Instances:
        - Small: m=100, n=200
        - Medium: m=300, n=600
        - Large: m=500, n=1000
    Each with density in {0.10, 0.20} and cap_ratio in {0.40, 0.60}
    
    Args:
        base_seed: Base random seed
    
    Returns:
        List of 12 SUKPInstance objects
    """
    instances = []
    seed_counter = base_seed
    
    sizes = [
        (100, 200, "Small"),
        (300, 600, "Medium"),
        (500, 1000, "Large")
    ]
    densities = [0.10, 0.20]
    cap_ratios = [0.40, 0.60]
    
    for m, n, size_name in sizes:
        for density in densities:
            for cap_ratio in cap_ratios:
                instance = generate_sukp_instance(
                    m=m,
                    n=n,
                    density=density,
                    cap_ratio=cap_ratio,
                    seed=seed_counter
                )
                instances.append(instance)
                seed_counter += 1
    
    return instances

