"""
Standalone (μ+λ) Evolution Strategy for Job Shop Scheduling.

Usage:
    python es.py jobshop.txt ft06
    python es.py new_instance.txt
"""

import sys
import random
from utils import (parse_instances, parse_single_instance,
                   make_random_solution, compute_makespan, get_neighbor,
                   decode_solution, plot_gantt)


def mutate(solution, strength=1):
    """
    Mutate a solution by applying 'strength' random neighbor swaps.
    Higher strength = more exploration.
    """
    mutant = solution.copy()
    for _ in range(strength):
        mutant = get_neighbor(mutant)
    return mutant


def evolution_strategy(instance, mu=10, lam=30, generations=500,
                       initial_strength=5, seed=None):
    """
    (μ+λ) Evolution Strategy for Job Shop Scheduling.

    How it works:
        1. Create μ random parent solutions
        2. Each generation: mutate parents to produce λ offspring
        3. Select the μ best from parents + offspring combined
        4. Repeat for 'generations' iterations

    Mutation strength adapts using Rechenberg's 1/5 success rule:
        - If > 1/5 of offspring improve on their parent → increase strength
        - If < 1/5 of offspring improve → decrease strength

    Args:
        instance:          dict with 'num_jobs', 'num_machines', 'jobs'
        mu:                number of parents (selected survivors)
        lam:               number of offspring per generation (λ)
        generations:       number of generations
        initial_strength:  starting mutation strength (number of swaps)
        seed:              random seed for reproducibility

    Returns:
        best_solution, best_makespan, history
    """
    if seed is not None:
        random.seed(seed)

    num_jobs = instance['num_jobs']
    num_machines = instance['num_machines']

    # --- Step 1: Initialize μ random parents ---
    population = []
    for _ in range(mu):
        sol = make_random_solution(num_jobs, num_machines)
        cost = compute_makespan(sol, instance)
        population.append((sol, cost))

    # Sort by cost (best first)
    population.sort(key=lambda x: x[1])

    best_sol = population[0][0].copy()
    best_cost = population[0][1]

    strength = initial_strength
    history = {
        'best_cost': [best_cost],
        'avg_cost': [sum(c for _, c in population) / len(population)],
        'strength': [strength]
    }

    # --- Step 2: Main loop ---
    for gen in range(generations):
        offspring = []
        successes = 0

        # Generate λ offspring by mutating random parents
        for _ in range(lam):
            # Pick a random parent from the μ best
            parent_sol, parent_cost = random.choice(population[:mu])

            # Mutate with current strength
            child_sol = mutate(parent_sol, strength=max(1, int(strength)))
            child_cost = compute_makespan(child_sol, instance)

            offspring.append((child_sol, child_cost))

            # Count successes for the 1/5 rule
            if child_cost < parent_cost:
                successes += 1

        # --- Step 3: Select μ best from parents + offspring (the "+" strategy) ---
        combined = population + offspring
        combined.sort(key=lambda x: x[1])
        population = combined[:mu]

        # Update best
        if population[0][1] < best_cost:
            best_sol = population[0][0].copy()
            best_cost = population[0][1]

        # --- Step 4: Adapt mutation strength (Rechenberg's 1/5 rule) ---
        success_rate = successes / lam
        if success_rate > 1/5:
            strength *= 1.2   # Too much exploitation: increase exploration
        elif success_rate < 1/5:
            strength *= 0.85  # Too much exploration: decrease
        strength = max(1, min(strength, 20))  # Clamp to [1, 20]

        # Record history
        avg_cost = sum(c for _, c in population) / len(population)
        history['best_cost'].append(best_cost)
        history['avg_cost'].append(avg_cost)
        history['strength'].append(strength)

    return best_sol, best_cost, history


# =============================================================================
# CLI
# =============================================================================

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python es.py <instance_file> [instance_name]")
        print("  python es.py jobshop.txt ft06")
        print("  python es.py new_instance.txt")
        sys.exit(1)

    filepath = sys.argv[1]
    instance_name = sys.argv[2] if len(sys.argv) > 2 else None

    if instance_name:
        instances = parse_instances(filepath)
        if instance_name not in instances:
            print(f"Instance '{instance_name}' not found. Available: {list(instances.keys())}")
            sys.exit(1)
        instance = instances[instance_name]
    else:
        instance = parse_single_instance(filepath)

    print(f"Instance: {instance['num_jobs']} jobs × {instance['num_machines']} machines")

    best_sol, best_ms, history = evolution_strategy(
        instance,
        mu=15,
        lam=50,
        generations=3000,
        initial_strength=5,
        seed=42
    )

    print(f"Best makespan: {best_ms}")
    print(f"Final mutation strength: {history['strength'][-1]:.2f}")

    schedule, _ = decode_solution(best_sol, instance)
    print("\nSchedule (job, op, machine, start, end):")
    for entry in sorted(schedule, key=lambda x: (x[2], x[3])):
        print(f"  Job {entry[0]:2d}, Op {entry[1]:2d} → Machine {entry[2]:2d}  [{entry[3]:5d} - {entry[4]:5d}]")

    # Show Gantt chart
    title = f"ES (μ+λ) — {instance_name or filepath}"
    plot_gantt(best_sol, instance, title=title)
