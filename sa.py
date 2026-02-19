"""
Standalone Simulated Annealing for Job Shop Scheduling.

Usage:
    python sa.py jobshop.txt ft06
    python sa.py new_instance.txt
"""

import sys
import math
import random
from utils import (parse_instances, parse_single_instance,
                   make_random_solution, compute_makespan, get_neighbor,
                   decode_solution, plot_gantt)


def simulated_annealing(instance, T_start=100.0, T_min=0.1, alpha=0.995,
                        max_iter=1000, seed=None):
    """
    Simulated Annealing for Job Shop Scheduling.

    Args:
        instance:  dict with 'num_jobs', 'num_machines', 'jobs'
        T_start:   initial temperature (high = more exploration)
        T_min:     minimum temperature (stopping criterion)
        alpha:     cooling rate (geometric schedule: T_new = alpha * T)
        max_iter:  neighbor evaluations per temperature step
        seed:      random seed for reproducibility

    Returns:
        best_solution, best_makespan, history
    """
    if seed is not None:
        random.seed(seed)

    num_jobs = instance['num_jobs']
    num_machines = instance['num_machines']

    # Initial random solution
    current = make_random_solution(num_jobs, num_machines)
    current_cost = compute_makespan(current, instance)

    best = current.copy()
    best_cost = current_cost

    history = {
        'current_cost': [current_cost],
        'best_cost': [best_cost],
        'temperature': [T_start],
        'accepted_worse': 0,
        'total_moves': 0
    }

    T = T_start

    while T > T_min:
        for _ in range(max_iter):
            neighbor = get_neighbor(current)
            neighbor_cost = compute_makespan(neighbor, instance)

            delta = neighbor_cost - current_cost

            if delta < 0:
                # Better → always accept
                current = neighbor
                current_cost = neighbor_cost
            else:
                # Worse → accept with probability e^(-delta / T) (Metropolis criterion)
                probability = math.exp(-delta / T)
                if random.random() < probability:
                    current = neighbor
                    current_cost = neighbor_cost
                    history['accepted_worse'] += 1

            history['total_moves'] += 1

            if current_cost < best_cost:
                best = current.copy()
                best_cost = current_cost

        history['current_cost'].append(current_cost)
        history['best_cost'].append(best_cost)
        history['temperature'].append(T)

        T *= alpha  # Geometric cooling

    return best, best_cost, history


# =============================================================================
# CLI
# =============================================================================

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python sa.py <instance_file> [instance_name]")
        print("  python sa.py jobshop.txt ft06")
        print("  python sa.py new_instance.txt")
        sys.exit(1)

    filepath = sys.argv[1]
    instance_name = sys.argv[2] if len(sys.argv) > 2 else None

    # Load instance
    if instance_name:
        instances = parse_instances(filepath)
        if instance_name not in instances:
            print(f"Instance '{instance_name}' not found. Available: {list(instances.keys())}")
            sys.exit(1)
        instance = instances[instance_name]
    else:
        instance = parse_single_instance(filepath)

    print(f"Instance: {instance['num_jobs']} jobs × {instance['num_machines']} machines")

    # Run SA
    best_sol, best_ms, history = simulated_annealing(
        instance,
        T_start=200,
        T_min=0.01,
        alpha=0.997,
        max_iter=1000,
        seed=42
    )

    print(f"Best makespan: {best_ms}")
    print(f"Total moves: {history['total_moves']}")
    print(f"Worse accepted: {history['accepted_worse']}")

    # Print schedule
    schedule, _ = decode_solution(best_sol, instance)
    print("\nSchedule (job, op, machine, start, end):")
    for entry in sorted(schedule, key=lambda x: (x[2], x[3])):
        print(f"  Job {entry[0]:2d}, Op {entry[1]:2d} → Machine {entry[2]:2d}  [{entry[3]:5d} - {entry[4]:5d}]")

    # Show Gantt chart
    title = f"SA — {instance_name or filepath}"
    plot_gantt(best_sol, instance, title=title)
