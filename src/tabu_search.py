"""Tabu Search implementation for SUKP."""

import random
import time
from typing import List, Optional
from .sukp_instance import SUKPInstance
from .evaluator import IncrementalEvaluator


class TabuSearch:
    """Tabu Search solver for SUKP."""
    
    def __init__(
        self,
        instance: SUKPInstance,
        lambda_penalty: float = 1000.0,
        max_iter: int = 10000,
        time_limit_sec: float = 300.0,
        candidate_size: int = 200,
        tabu_tenure: int = 10,
        tenure_mode: str = "fixed",
        stagnation_limit: Optional[int] = None,
        seed: Optional[int] = None
    ):
        """Initialize Tabu Search solver.
        
        Args:
            instance: SUKP instance to solve
            lambda_penalty: Penalty coefficient for constraint violations
            max_iter: Maximum number of iterations
            time_limit_sec: Time limit in seconds
            candidate_size: Number of candidate moves to evaluate per iteration
            tabu_tenure: Tabu tenure (used if tenure_mode is "fixed")
            tenure_mode: "fixed" or "random" (random uses [7, 15])
            stagnation_limit: Stop if no improvement for this many iterations (None to disable)
            seed: Random seed for reproducibility
        """
        self.instance = instance
        self.lambda_penalty = lambda_penalty
        self.max_iter = max_iter
        self.time_limit_sec = time_limit_sec
        # Reduce candidate size for large instances
        if instance.n > 500:
            self.candidate_size = min(candidate_size, 50)
        elif instance.n > 300:
            self.candidate_size = min(candidate_size, 100)
        else:
            self.candidate_size = candidate_size
        self.tabu_tenure = tabu_tenure
        self.tenure_mode = tenure_mode
        self.stagnation_limit = stagnation_limit
        self.seed = seed
        
        if seed is not None:
            random.seed(seed)
        
        self.evaluator = IncrementalEvaluator(instance, lambda_penalty)
        self.tabu_list: List[int] = []  # Tabu attributes (set indices)
        self.tabu_until: List[int] = []  # Iteration until tabu expires
        
        # Statistics
        self.iterations: int = 0
        self.start_time: float = 0.0
        self.best_iteration: int = 0
    
    def solve(self, initial_solution: Optional[List[bool]] = None) -> dict:
        """Run Tabu Search.
        
        Args:
            initial_solution: Initial solution (empty feasible if None, then greedy construction)
        
        Returns:
            Dictionary with solution and statistics
        """
        # Initialize with empty feasible solution
        if initial_solution is None:
            initial_solution = self._generate_initial_solution()
        
        self.evaluator.reset(initial_solution)
        self.tabu_list = []
        self.tabu_until = []
        self.iterations = 0
        self.start_time = time.time()
        self.best_iteration = 0
        
        # Main loop
        while not self._should_stop():
            # Check time limit before iteration
            if time.time() - self.start_time >= self.time_limit_sec:
                break
            
            # Update tabu list
            self._update_tabu_list()
            
            # Select best admissible move (with time checks)
            move = self._select_move()
            if move is None:
                break  # No admissible move found
            
            # Check time limit after move selection
            if time.time() - self.start_time >= self.time_limit_sec:
                break
            
            # Track best score before move
            old_best_score = self.evaluator.best_penalized_score
            
            # Apply move
            self.evaluator.apply_move(move)
            
            # Update tabu
            tenure = self._get_tenure()
            self._add_to_tabu(move, tenure)
            
            # Update statistics
            self.iterations += 1
            
            # Check if we improved
            if self.evaluator.best_penalized_score > old_best_score + 1e-6:
                self.best_iteration = self.iterations
        
        elapsed_time = time.time() - self.start_time
        
        return {
            'solution': self.evaluator.best_solution.copy(),
            'best_penalized_score': self.evaluator.best_penalized_score,
            'best_feasible_profit': self.evaluator.best_feasible_profit,
            'iterations': self.iterations,
            'time_sec': elapsed_time,
            'best_iteration': self.best_iteration
        }
    
    def _generate_initial_solution(self) -> List[bool]:
        """Generate initial feasible solution.
        
        Starts from empty solution (all False), then applies greedy construction.
        """
        # Start with empty solution (guaranteed feasible)
        solution = [False] * self.instance.n
        
        # Track covered elements and current union weight for greedy construction
        covered = [False] * self.instance.m
        current_weight = 0.0
        
        # Greedy feasible construction: add sets by profit/weight ratio
        # Compute ratios for all sets
        set_ratios = []
        for i in range(self.instance.n):
            # Compute weight that would be added if set i is added to current solution
            added_weight = sum(
                self.instance.weights[j] 
                for j in self.instance.sets[i] 
                if not covered[j]
            )
            if added_weight > 0:
                ratio = self.instance.profits[i] / added_weight
            else:
                # Set adds no new weight (all elements already covered)
                ratio = float('inf') if self.instance.profits[i] > 0 else 0.0
            set_ratios.append((ratio, i, added_weight))
        
        # Sort by ratio (descending)
        set_ratios.sort(reverse=True, key=lambda x: x[0])
        
        # Greedily add sets while maintaining feasibility
        for ratio, i, added_weight in set_ratios:
            if current_weight + added_weight <= self.instance.capacity:
                solution[i] = True
                current_weight += added_weight
                # Update covered elements
                for j in self.instance.sets[i]:
                    covered[j] = True
        
        return solution
    
    def _should_stop(self) -> bool:
        """Check if search should stop."""
        # Time limit
        if time.time() - self.start_time >= self.time_limit_sec:
            return True
        
        # Iteration limit
        if self.iterations >= self.max_iter:
            return True
        
        # Stagnation limit
        if self.stagnation_limit is not None:
            if self.iterations - self.best_iteration >= self.stagnation_limit:
                return True
        
        return False
    
    def _update_tabu_list(self) -> None:
        """Remove expired tabu attributes."""
        # Remove expired entries
        expired = [i for i, until in enumerate(self.tabu_until) if until <= self.iterations]
        for idx in reversed(expired):
            self.tabu_list.pop(idx)
            self.tabu_until.pop(idx)
    
    def _get_tenure(self) -> int:
        """Get tabu tenure for next move."""
        if self.tenure_mode == "random":
            return random.randint(7, 15)
        else:
            return self.tabu_tenure
    
    def _add_to_tabu(self, move: int, tenure: int) -> None:
        """Add move to tabu list."""
        self.tabu_list.append(move)
        self.tabu_until.append(self.iterations + tenure)
    
    def _is_tabu(self, move: int) -> bool:
        """Check if move is tabu."""
        return move in self.tabu_list
    
    def _check_aspiration(self, move: int) -> bool:
        """Check if tabu move satisfies aspiration criterion.
        
        Aspiration: allow tabu move if it produces better penalized score
        than best-so-far.
        """
        if not self._is_tabu(move):
            return True
        
        # Evaluate move
        _, _, delta_score = self.evaluator.evaluate_move(move)
        new_score = self.evaluator.get_penalized_score() + delta_score
        
        return new_score > self.evaluator.best_penalized_score
    
    def _select_move(self) -> Optional[int]:
        """Select best admissible move from candidate list.
        
        Returns:
            Best move index, or None if no admissible move found
        """
        # Sample candidate moves
        candidates = random.sample(
            range(self.instance.n),
            min(self.candidate_size, self.instance.n)
        )
        
        best_move = None
        best_score = float('-inf')
        
        for move in candidates:
            # Check time limit during candidate evaluation
            if time.time() - self.start_time >= self.time_limit_sec:
                # Return best found so far if time limit exceeded
                break
            
            # Check if admissible (not tabu or satisfies aspiration)
            if not self._check_aspiration(move):
                continue
            
            # Evaluate move
            _, _, delta_score = self.evaluator.evaluate_move(move)
            new_score = self.evaluator.get_penalized_score() + delta_score
            
            if new_score > best_score:
                best_score = new_score
                best_move = move
        
        return best_move

