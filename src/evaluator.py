"""Incremental evaluation for SUKP solutions."""

from typing import List, Tuple
from .sukp_instance import SUKPInstance


class IncrementalEvaluator:
    """Efficient incremental evaluation of SUKP solutions.
    
    Maintains element coverage counts and current solution state
    to enable O(|set_i|) evaluation of moves instead of O(m).
    """
    
    def __init__(self, instance: SUKPInstance, lambda_penalty: float = 1000.0):
        """Initialize evaluator.
        
        Args:
            instance: SUKP instance
            lambda_penalty: Penalty coefficient for constraint violations
        """
        self.instance = instance
        self.lambda_penalty = lambda_penalty
        
        # Current solution state
        self.solution: List[bool] = [False] * instance.n
        self.cover: List[int] = [0] * instance.m  # Coverage count for each element
        self.current_profit: float = 0.0
        self.current_union_weight: float = 0.0
        
        # Best solutions tracked
        self.best_penalized_score: float = float('-inf')
        self.best_feasible_profit: float = 0.0
        self.best_solution: List[bool] = [False] * instance.n
    
    def reset(self, initial_solution: List[bool] = None) -> None:
        """Reset evaluator to initial state.
        
        Args:
            initial_solution: Initial solution (all False if None)
        """
        if initial_solution is None:
            initial_solution = [False] * self.instance.n
        
        # Reset best solutions
        self.best_penalized_score = float('-inf')
        self.best_feasible_profit = 0.0
        self.best_solution = [False] * self.instance.n
        
        self.solution = initial_solution.copy()
        self.cover = [0] * self.instance.m
        self.current_profit = 0.0
        self.current_union_weight = 0.0
        
        # Compute initial state
        for i in range(self.instance.n):
            if self.solution[i]:
                self._add_set(i)
        
        # Update best
        self._update_best()
    
    def _add_set(self, i: int) -> None:
        """Add set i to current solution (internal, no checks)."""
        self.current_profit += self.instance.profits[i]
        for j in self.instance.sets[i]:
            if self.cover[j] == 0:
                self.current_union_weight += self.instance.weights[j]
            self.cover[j] += 1
    
    def _remove_set(self, i: int) -> None:
        """Remove set i from current solution (internal, no checks)."""
        self.current_profit -= self.instance.profits[i]
        for j in self.instance.sets[i]:
            self.cover[j] -= 1
            if self.cover[j] == 0:
                self.current_union_weight -= self.instance.weights[j]
    
    def evaluate_move(self, i: int) -> Tuple[float, float, float]:
        """Evaluate flipping set i.
        
        Args:
            i: Set index to flip
        
        Returns:
            Tuple of (delta_profit, delta_weight, delta_penalized_score)
        """
        if self.solution[i]:
            # Removing set i
            delta_profit = -self.instance.profits[i]
            delta_weight = 0.0
            for j in self.instance.sets[i]:
                if self.cover[j] == 1:  # Will become uncovered
                    delta_weight -= self.instance.weights[j]
        else:
            # Adding set i
            delta_profit = self.instance.profits[i]
            delta_weight = 0.0
            for j in self.instance.sets[i]:
                if self.cover[j] == 0:  # Will become newly covered
                    delta_weight += self.instance.weights[j]
        
        # Compute penalized score delta
        old_weight = self.current_union_weight
        new_weight = old_weight + delta_weight
        old_violation = max(0, old_weight - self.instance.capacity)
        new_violation = max(0, new_weight - self.instance.capacity)
        delta_penalty = self.lambda_penalty * (new_violation - old_violation)
        delta_penalized_score = delta_profit - delta_penalty
        
        return delta_profit, delta_weight, delta_penalized_score
    
    def apply_move(self, i: int) -> None:
        """Apply move (flip set i) to current solution.
        
        Args:
            i: Set index to flip
        """
        if self.solution[i]:
            self._remove_set(i)
        else:
            self._add_set(i)
        
        self.solution[i] = not self.solution[i]
        self._update_best()
    
    def _update_best(self) -> None:
        """Update best solutions if current is better."""
        penalized_score = self.get_penalized_score()
        if penalized_score > self.best_penalized_score:
            self.best_penalized_score = penalized_score
            self.best_solution = self.solution.copy()
        
        # Update best feasible profit independently if current is feasible
        # This ensures we track the best feasible solution regardless of penalized score
        if self.is_feasible():
            if self.current_profit > self.best_feasible_profit:
                self.best_feasible_profit = self.current_profit
    
    def get_penalized_score(self) -> float:
        """Get current penalized score."""
        violation = max(0, self.current_union_weight - self.instance.capacity)
        return self.current_profit - self.lambda_penalty * violation
    
    def is_feasible(self) -> bool:
        """Check if current solution is feasible."""
        return self.current_union_weight <= self.instance.capacity
    
    def get_current_profit(self) -> float:
        """Get current profit."""
        return self.current_profit
    
    def get_current_weight(self) -> float:
        """Get current union weight."""
        return self.current_union_weight

