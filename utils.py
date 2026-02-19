"""
Shared utilities for Job Shop Scheduling algorithms.
Includes: instance parser, solution encoding, makespan computation, and Gantt chart.
"""

import random
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


# =============================================================================
# 1. INSTANCE PARSING
# =============================================================================

def parse_instances(filepath):
    """
    Parse all instances from a jobshop.txt file.
    
    Returns:
        dict: {instance_name: {'num_jobs', 'num_machines', 'jobs'}}
              where jobs[j][k] = (machine_id, processing_time) for job j, operation k.
    """
    instances = {}

    with open(filepath, 'r') as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if line.startswith('instance '):
            name = line.split('instance ')[1].strip()

            i += 1
            while i < len(lines):
                line = lines[i].strip()
                i += 1
                if line == '' or line.startswith('+'):
                    continue
                parts = line.split()
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    num_jobs, num_machines = int(parts[0]), int(parts[1])
                    break

            jobs = []
            for _ in range(num_jobs):
                while i < len(lines):
                    line = lines[i].strip()
                    i += 1
                    if line and not line.startswith('+'):
                        break

                values = list(map(int, line.split()))
                operations = [(values[k], values[k + 1]) for k in range(0, len(values), 2)]
                jobs.append(operations)

            instances[name] = {
                'num_jobs': num_jobs,
                'num_machines': num_machines,
                'jobs': jobs
            }
        else:
            i += 1

    return instances


def parse_single_instance(filepath):
    """
    Parse a single instance file (just the dimensions line + job lines, no headers).
    Falls back to parse_instances if the file contains named instances.
    """
    with open(filepath, 'r') as f:
        lines = [l.strip() for l in f.readlines() if l.strip() and not l.strip().startswith('+')]

    # Check if file has named instances
    for line in lines:
        if line.startswith('instance '):
            all_instances = parse_instances(filepath)
            raise ValueError(
                f"File contains {len(all_instances)} named instances. "
                f"Specify one as a second argument.\n"
                f"Available: {', '.join(list(all_instances.keys())[:15])}..."
            )

    # Otherwise, parse as a single instance
    # Find the dimensions line (first line with exactly 2 integers)
    for idx, line in enumerate(lines):
        parts = line.split()
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            num_jobs, num_machines = int(parts[0]), int(parts[1])
            break
    else:
        raise ValueError("Could not find dimensions line (num_jobs num_machines)")

    jobs = []
    for j in range(num_jobs):
        values = list(map(int, lines[idx + 1 + j].split()))
        operations = [(values[k], values[k + 1]) for k in range(0, len(values), 2)]
        jobs.append(operations)

    return {'num_jobs': num_jobs, 'num_machines': num_machines, 'jobs': jobs}


# =============================================================================
# 2. SOLUTION REPRESENTATION
# =============================================================================

def make_random_solution(num_jobs, num_machines):
    """
    Create a random permutation-with-repetition solution.
    Each job ID appears num_machines times; we shuffle them randomly.
    
    Example for 3 jobs × 2 machines: [0, 1, 2, 0, 2, 1]
    → 1st op of job 0, 1st op of job 1, 1st op of job 2,
      2nd op of job 0, 2nd op of job 2, 2nd op of job 1
    """
    solution = []
    for job_id in range(num_jobs):
        solution.extend([job_id] * num_machines)
    random.shuffle(solution)
    return solution


# =============================================================================
# 3. DECODING & MAKESPAN
# =============================================================================

def decode_solution(solution, instance):
    """
    Decode a permutation-with-repetition into a full schedule.
    
    Returns:
        schedule: list of (job, op_index, machine, start, end)
        makespan: total completion time
    """
    jobs = instance['jobs']
    num_machines = instance['num_machines']

    job_op_count = [0] * len(jobs)
    job_end_time = [0] * len(jobs)
    machine_end_time = [0] * num_machines

    schedule = []

    for job_id in solution:
        op_idx = job_op_count[job_id]
        machine, duration = jobs[job_id][op_idx]

        start = max(job_end_time[job_id], machine_end_time[machine])
        end = start + duration

        schedule.append((job_id, op_idx, machine, start, end))

        job_end_time[job_id] = end
        machine_end_time[machine] = end
        job_op_count[job_id] = op_idx + 1

    makespan = max(machine_end_time)
    return schedule, makespan


def compute_makespan(solution, instance):
    _, makespan = decode_solution(solution, instance)
    return makespan


# =============================================================================
# 4. NEIGHBORHOOD
# =============================================================================

def get_neighbor(solution):
    """
    Generate a neighbor by swapping two adjacent elements
    that belong to different jobs.
    """
    neighbor = solution.copy()
    n = len(neighbor)

    attempts = 0
    while attempts < n:
        i = random.randint(0, n - 2)
        if neighbor[i] != neighbor[i + 1]:
            neighbor[i], neighbor[i + 1] = neighbor[i + 1], neighbor[i]
            return neighbor
        attempts += 1

    # Fallback: swap two random positions with different jobs
    # while True:
    #     i, j = random.sample(range(n), 2)
    #     if neighbor[i] != neighbor[j]:
    #         neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
    #         return neighbor


# =============================================================================
# 5. VISUALIZATION
# =============================================================================

def plot_gantt(solution, instance, title="Job Shop Schedule"):
    """Draw a Gantt chart showing which job runs on which machine and when."""
    schedule, makespan = decode_solution(solution, instance)
    num_machines = instance['num_machines']
    num_jobs = instance['num_jobs']

    cmap = plt.colormaps['tab20'].resampled(num_jobs)
    colors = [cmap(i) for i in range(num_jobs)]

    fig, ax = plt.subplots(figsize=(14, max(4, num_machines * 0.5)))

    for (job_id, op_idx, machine, start, end) in schedule:
        ax.barh(machine, end - start, left=start, height=0.6,
                color=colors[job_id], edgecolor='black', linewidth=0.5)
        if num_jobs <= 10:
            ax.text((start + end) / 2, machine, f'J{job_id}',
                    ha='center', va='center', fontsize=7, fontweight='bold')

    ax.set_xlabel('Time')
    ax.set_ylabel('Machine')
    ax.set_yticks(range(num_machines))
    ax.set_yticklabels([f'M{m}' for m in range(num_machines)])
    ax.set_title(f'{title} — Makespan = {makespan}')
    ax.invert_yaxis()

    if num_jobs <= 20:
        patches = [mpatches.Patch(color=colors[j], label=f'Job {j}') for j in range(num_jobs)]
        ax.legend(handles=patches, bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=7)

    plt.tight_layout()
    plt.show()


def plot_convergence(history, title="Convergence"):
    """Plot makespan and temperature over iterations."""
    fig, ax1 = plt.subplots(figsize=(10, 5))

    steps = range(len(history['best_cost']))

    if 'current_cost' in history:
        ax1.plot(steps, history['current_cost'], alpha=0.4, color='steelblue', label='Current cost')
    ax1.plot(steps, history['best_cost'], color='darkred', linewidth=2, label='Best cost')
    ax1.set_xlabel('Iteration')
    ax1.set_ylabel('Makespan')
    ax1.legend(loc='upper left')

    if 'temperature' in history:
        ax2 = ax1.twinx()
        ax2.plot(steps, history['temperature'], color='orange', linestyle='--', alpha=0.6, label='Temperature')
        ax2.set_ylabel('Temperature')
        ax2.legend(loc='upper right')

    plt.title(title)
    plt.tight_layout()
    plt.show()
