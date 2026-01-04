# SUKP Tabu Search

A Python implementation of Tabu Search for solving the **Set Union Knapsack Problem (SUKP)**.

## Problem Description

The Set Union Knapsack Problem (SUKP) is a combinatorial optimization problem defined as follows:

- **Elements**: There are `m` elements, each with a weight `w[j] > 0` (j = 0, ..., m-1)
- **Sets**: There are `n` sets, each with a profit `p[i] > 0` (i = 0, ..., n-1)
- **Membership**: Each set `i` contains a list of element indices `sets[i]`
- **Solution**: A binary vector `x` of length `n`, where `x[i] = 1` means set `i` is selected
- **Union Weight**: The weight of the solution is the sum of weights of **unique** elements covered by selected sets
- **Objective**: Maximize the sum of profits of selected sets
- **Constraint**: The union weight must not exceed capacity `C`

### Penalty-Based Constraint Handling

Since SUKP is a constrained optimization problem, we use a penalty-based approach:

```
F(x) = profit(x) - λ × max(0, union_weight(x) - C)
```

where `λ` is the penalty coefficient (default: 1000.0).

## Dataset Generation

The project generates synthetic SUKP instances with the following characteristics:

### Instance Sizes
- **Small**: m=100, n=200
- **Medium**: m=300, n=600
- **Large**: m=500, n=1000

### Parameters
- **Density**: Probability that an element belongs to a set (0.10, 0.20)
- **Capacity Ratio**: Capacity = cap_ratio × sum(all_element_weights) (0.40, 0.60)

This produces **12 instances total** (3 sizes × 2 densities × 2 capacity ratios).

### Instance Naming
Instances are saved with the naming scheme:
```
m{m}_n{n}_d{density}_c{cap_ratio}_seed{seed}.json
```

For example: `m100_n200_d010_c040_seed42.json`

## Tabu Search Algorithm

### Key Features

1. **Incremental Evaluation**: Efficient O(|set_i|) move evaluation by maintaining element coverage counts
2. **Move Operator**: 1-flip (toggle a set's selection)
3. **Tabu List**: Move-based tabu (forbids flipping recently flipped sets)
4. **Tabu Tenure**: 
   - Fixed mode: constant tenure (default: 10)
   - Random mode: random tenure in [7, 15] per move
5. **Aspiration Criterion**: Allow tabu move if it produces better penalized score than best-so-far
6. **Candidate List**: Sample K distinct sets per iteration (default: K=200), evaluate each, select best admissible
7. **Stopping Criteria**:
   - Maximum iterations (default: 10000)
   - Time limit in seconds (default: 300.0)
   - Optional stagnation limit (no improvement for S iterations)

### Solution Tracking

The algorithm tracks:
- **Best penalized score**: Best solution by penalized objective (may be infeasible)
- **Best feasible profit**: Best profit among feasible solutions found

## Installation

1. Clone or download this repository
2. Ensure Python 3.11+ is installed
3. No external dependencies required (uses only Python standard library)

```bash
cd sukp-tabu-search
```

## Usage

### Generate Instances

Generate all 12 instances:

```bash
python -m src.experiment --generate --seed 42
```

Instances will be saved to `data/instances/`.

### Run Experiments

Run experiments on all instances (5 runs per instance by default):

```bash
python -m src.experiment --generate --run --seed 42
```

### Customize Parameters

```bash
python -m src.experiment \
    --generate \
    --run \
    --seed 42 \
    --max-iter 20000 \
    --time-limit 600.0 \
    --candidate-size 300 \
    --tabu-tenure 15 \
    --tenure-mode random \
    --lambda-penalty 2000.0 \
    --runs-per-instance 10 \
    --out data/results
```

### Command-Line Arguments

- `--seed`: Base random seed (default: 42)
- `--out`: Output directory for results (default: data/results)
- `--generate`: Generate instances before running
- `--run`: Run experiments
- `--instances-dir`: Directory for instance files (default: data/instances)
- `--max-iter`: Maximum iterations per run (default: 10000)
- `--time-limit`: Time limit per run in seconds (default: 300.0)
- `--candidate-size`: Candidate list size (default: 200)
- `--tabu-tenure`: Tabu tenure (default: 10)
- `--tenure-mode`: Tenure mode: fixed or random (default: fixed)
- `--lambda-penalty`: Penalty coefficient (default: 1000.0)
- `--runs-per-instance`: Number of runs per instance (default: 5)
- `--stagnation-limit`: Stagnation limit iterations (None to disable)

## Output Files

### Instance Files
Generated instances are saved as JSON files in `data/instances/`:
```json
{
  "m": 100,
  "n": 200,
  "weights": [1.0, 2.0, ...],
  "profits": [10.0, 20.0, ...],
  "sets": [[0, 1, 5], [2, 3], ...],
  "capacity": 5000.0,
  "density": 0.1,
  "cap_ratio": 0.4,
  "seed": 42
}
```

### Results Files

#### `results.csv`
Detailed results for each run:
- `instance`: Instance name
- `m`, `n`: Problem dimensions
- `density`, `cap_ratio`: Instance parameters
- `run`: Run number (1-5)
- `best_feasible_profit`: Best feasible profit found
- `best_penalized_score`: Best penalized score found
- `time_sec`: Runtime in seconds
- `iters`: Number of iterations

#### `results_summary.csv`
Summary statistics per instance:
- `instance`: Instance name
- `m`, `n`: Problem dimensions
- `density`, `cap_ratio`: Instance parameters
- `mean_best_feasible_profit`: Mean best feasible profit across runs
- `best_overall_feasible_profit`: Best feasible profit across all runs
- `std_best_feasible_profit`: Standard deviation of best feasible profit
- `avg_time_sec`: Average runtime across runs
- `best_time_sec`: Best (minimum) runtime across runs

## Project Structure

```
sukp-tabu-search/
├── README.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── sukp_instance.py      # Instance data model and I/O
│   ├── generator.py           # Instance generation
│   ├── evaluator.py           # Incremental evaluation
│   ├── tabu_search.py         # Tabu Search algorithm
│   ├── experiment.py          # Experiment runner
│   └── utils.py               # Utility functions
├── data/
│   ├── instances/             # Generated instance files
│   └── results/               # Experiment results
```

## Code Quality

- **Type hints**: All functions include type annotations
- **Dataclasses**: Used for instance representation
- **Docstrings**: Comprehensive documentation
- **Modular design**: Clean separation of concerns
- **Reproducibility**: Seed-based random number generation

## Example Workflow

1. **Generate instances**:
   ```bash
   python -m src.experiment --generate --seed 42
   ```

2. **Run experiments**:
   ```bash
   python -m src.experiment --run --seed 42 --max-iter 10000 --time-limit 300
   ```

3. **Analyze results**:
   - Check `data/results/results.csv` for detailed per-run data
   - Check `data/results/results_summary.csv` for aggregated statistics

## Notes

- The implementation uses **incremental evaluation** to avoid recomputing union weights from scratch for each move, achieving O(|set_i|) complexity per move evaluation.
- The algorithm tracks both **penalized scores** (for search guidance) and **feasible profits** (for final reporting).
- All random operations are seeded for reproducibility.
- The code is designed to be efficient and scalable for large instances.

## License

This project is provided as-is for educational and research purposes.

