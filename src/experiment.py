"""Experiment runner for SUKP Tabu Search."""

import argparse
import csv
import os
import time
from typing import List, Dict
from .sukp_instance import SUKPInstance
from .generator import generate_all_instances
from .tabu_search import TabuSearch
from .utils import save_instances, load_instances, get_instance_filename, ensure_dir


def run_experiments(
    instances: List[SUKPInstance],
    runs_per_instance: int = 5,
    max_iter: int = 10000,
    time_limit_sec: float = 300.0,
    candidate_size: int = 200,
    tabu_tenure: int = 10,
    tenure_mode: str = "fixed",
    lambda_penalty: float = 1000.0,
    stagnation_limit: int = None,
    base_seed: int = 42,
    output_dir: str = "data/results"
) -> None:
    """Run experiments on all instances.
    
    Args:
        instances: List of SUKP instances
        runs_per_instance: Number of runs per instance
        max_iter: Maximum iterations per run
        time_limit_sec: Time limit per run (seconds)
        candidate_size: Candidate list size
        tabu_tenure: Tabu tenure
        tenure_mode: "fixed" or "random"
        lambda_penalty: Penalty coefficient
        stagnation_limit: Stagnation limit (None to disable)
        base_seed: Base random seed
        output_dir: Output directory for results
    """
    ensure_dir(output_dir)
    
    results = []
    
    for instance_idx, instance in enumerate(instances):
        print(f"\n{'='*60}")
        print(f"Instance {instance_idx + 1}/{len(instances)}: {get_instance_filename(instance)}")
        print(f"{'='*60}")
        
        for run_id in range(runs_per_instance):
            run_seed = base_seed + instance_idx * 1000 + run_id
            
            print(f"\nRun {run_id + 1}/{runs_per_instance} (seed={run_seed})")
            
            # Create solver
            solver = TabuSearch(
                instance=instance,
                lambda_penalty=lambda_penalty,
                max_iter=max_iter,
                time_limit_sec=time_limit_sec,
                candidate_size=candidate_size,
                tabu_tenure=tabu_tenure,
                tenure_mode=tenure_mode,
                stagnation_limit=stagnation_limit,
                seed=run_seed
            )
            
            # Solve
            start_time = time.time()
            result = solver.solve()
            elapsed = time.time() - start_time
            
            # Store results
            instance_name = get_instance_filename(instance).replace('.json', '')
            results.append({
                'instance': instance_name,
                'm': instance.m,
                'n': instance.n,
                'density': instance.density,
                'cap_ratio': instance.cap_ratio,
                'run': run_id + 1,
                'best_feasible_profit': result['best_feasible_profit'],
                'best_penalized_score': result['best_penalized_score'],
                'time_sec': result['time_sec'],
                'iters': result['iterations']
            })
            
            print(f"  Best feasible profit: {result['best_feasible_profit']:.2f}")
            print(f"  Best penalized score: {result['best_penalized_score']:.2f}")
            print(f"  Time: {result['time_sec']:.2f}s, Iterations: {result['iterations']}")
    
    # Save detailed results
    results_file = os.path.join(output_dir, 'results.csv')
    save_results_csv(results, results_file)
    print(f"\n{'='*60}")
    print(f"Saved detailed results to: {results_file}")
    
    # Compute and save summary
    summary_file = os.path.join(output_dir, 'results_summary.csv')
    save_summary_csv(results, summary_file)
    print(f"Saved summary to: {summary_file}")


def save_results_csv(results: List[Dict], filepath: str) -> None:
    """Save detailed results to CSV."""
    if not results:
        return
    
    fieldnames = [
        'instance', 'm', 'n', 'density', 'cap_ratio', 'run',
        'best_feasible_profit', 'best_penalized_score', 'time_sec', 'iters'
    ]
    
    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def save_summary_csv(results: List[Dict], filepath: str) -> None:
    """Compute and save summary statistics."""
    if not results:
        return
    
    # Group by instance
    instance_data: Dict[str, List[Dict]] = {}
    for result in results:
        instance = result['instance']
        if instance not in instance_data:
            instance_data[instance] = []
        instance_data[instance].append(result)
    
    # Compute statistics per instance
    summary = []
    for instance, runs in instance_data.items():
        profits = [r['best_feasible_profit'] for r in runs]
        times = [r['time_sec'] for r in runs]
        
        mean_profit = sum(profits) / len(profits)
        best_profit = max(profits)
        std_profit = (
            (sum((p - mean_profit) ** 2 for p in profits) / len(profits)) ** 0.5
            if len(profits) > 1 else 0.0
        )
        avg_time = sum(times) / len(times)
        best_time = min(times)
        
        # Get instance parameters from first run
        first_run = runs[0]
        summary.append({
            'instance': instance,
            'm': first_run['m'],
            'n': first_run['n'],
            'density': first_run['density'],
            'cap_ratio': first_run['cap_ratio'],
            'mean_best_feasible_profit': mean_profit,
            'best_overall_feasible_profit': best_profit,
            'std_best_feasible_profit': std_profit,
            'avg_time_sec': avg_time,
            'best_time_sec': best_time
        })
    
    # Sort by instance name
    summary.sort(key=lambda x: x['instance'])
    
    # Save
    fieldnames = [
        'instance', 'm', 'n', 'density', 'cap_ratio',
        'mean_best_feasible_profit', 'best_overall_feasible_profit',
        'std_best_feasible_profit', 'avg_time_sec', 'best_time_sec'
    ]
    
    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary)


def main():
    """Main entry point for experiments."""
    parser = argparse.ArgumentParser(
        description='Run Tabu Search experiments on SUKP instances'
    )
    parser.add_argument('--seed', type=int, default=42,
                        help='Base random seed (default: 42)')
    parser.add_argument('--out', type=str, default='data/results',
                        help='Output directory for results (default: data/results)')
    parser.add_argument('--generate', action='store_true',
                        help='Generate instances before running')
    parser.add_argument('--run', action='store_true',
                        help='Run experiments')
    parser.add_argument('--instances-dir', type=str, default='data/instances',
                        help='Directory for instance files (default: data/instances)')
    parser.add_argument('--max-iter', type=int, default=10000,
                        help='Maximum iterations per run (default: 10000)')
    parser.add_argument('--time-limit', type=float, default=300.0,
                        help='Time limit per run in seconds (default: 300.0)')
    parser.add_argument('--candidate-size', type=int, default=200,
                        help='Candidate list size (default: 200)')
    parser.add_argument('--tabu-tenure', type=int, default=10,
                        help='Tabu tenure (default: 10)')
    parser.add_argument('--tenure-mode', type=str, default='fixed',
                        choices=['fixed', 'random'],
                        help='Tenure mode: fixed or random (default: fixed)')
    parser.add_argument('--lambda-penalty', type=float, default=1000.0,
                        help='Penalty coefficient (default: 1000.0)')
    parser.add_argument('--runs-per-instance', type=int, default=5,
                        help='Number of runs per instance (default: 5)')
    parser.add_argument('--stagnation-limit', type=int, default=None,
                        help='Stagnation limit (None to disable)')
    
    args = parser.parse_args()
    
    instances = []
    
    # Generate instances if requested
    if args.generate:
        print("Generating instances...")
        instances = generate_all_instances(base_seed=args.seed)
        ensure_dir(args.instances_dir)
        save_instances(instances, args.instances_dir)
        print(f"\nGenerated {len(instances)} instances")
    
    # Load instances if not generated
    if not instances:
        if os.path.exists(args.instances_dir):
            print(f"Loading instances from {args.instances_dir}...")
            instances = load_instances(args.instances_dir)
            print(f"Loaded {len(instances)} instances")
        else:
            print("No instances found. Use --generate to create instances.")
            return
    
    # Run experiments if requested
    if args.run:
        run_experiments(
            instances=instances,
            runs_per_instance=args.runs_per_instance,
            max_iter=args.max_iter,
            time_limit_sec=args.time_limit,
            candidate_size=args.candidate_size,
            tabu_tenure=args.tabu_tenure,
            tenure_mode=args.tenure_mode,
            lambda_penalty=args.lambda_penalty,
            stagnation_limit=args.stagnation_limit,
            base_seed=args.seed,
            output_dir=args.out
        )
    else:
        print("Use --run to execute experiments.")


if __name__ == '__main__':
    main()

