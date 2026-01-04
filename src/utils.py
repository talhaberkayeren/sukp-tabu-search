"""Utility functions."""

import os
from pathlib import Path
from typing import List
from .sukp_instance import SUKPInstance


def get_instance_filename(instance: SUKPInstance) -> str:
    """Generate filename for instance.
    
    Format: m{m}_n{n}_d{density}_c{cap_ratio}_seed{seed}.json
    """
    density_str = f"{instance.density:.2f}".replace('.', '')
    cap_str = f"{instance.cap_ratio:.2f}".replace('.', '')
    return f"m{instance.m}_n{instance.n}_d{density_str}_c{cap_str}_seed{instance.seed}.json"


def ensure_dir(path: str) -> None:
    """Ensure directory exists, create if not."""
    Path(path).mkdir(parents=True, exist_ok=True)


def save_instances(instances: List[SUKPInstance], output_dir: str) -> None:
    """Save all instances to JSON files.
    
    Args:
        instances: List of SUKPInstance objects
        output_dir: Output directory path
    """
    ensure_dir(output_dir)
    for instance in instances:
        filename = get_instance_filename(instance)
        filepath = os.path.join(output_dir, filename)
        instance.save(filepath)
        print(f"Saved instance: {filename}")


def load_instances(input_dir: str) -> List[SUKPInstance]:
    """Load all instances from directory.
    
    Args:
        input_dir: Input directory path
    
    Returns:
        List of SUKPInstance objects
    """
    instances = []
    for filename in sorted(os.listdir(input_dir)):
        if filename.endswith('.json'):
            filepath = os.path.join(input_dir, filename)
            instance = SUKPInstance.load(filepath)
            instances.append(instance)
    return instances

