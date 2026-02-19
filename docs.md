# Function Documentation

## utils.py

### `parse_instances(filepath)`
Parse all instances from a jobshop.txt file.
Returns: dict {instance_name: {'num_jobs', 'num_machines', 'jobs'}}
where jobs[j][k] = (machine_id, processing_time) for job j, operation k.

### `parse_single_instance(filepath)`
Parse a file containing a single unnamed instance.
Returns: dict with 'num_jobs', 'num_machines', 'jobs'.
Raises ValueError if file contains named instances.

### `make_random_solution(num_jobs, num_machines)`
Create a random permutation-with-repetition solution.
Each job ID appears num_machines times; we shuffle them randomly.
Example for 3 jobs × 2 machines: [0, 1, 2, 0, 2, 1]

### `decode_solution(solution, instance)`
Decode a permutation-with-repetition into a full schedule.
Returns: schedule (list of (job, op_index, machine, start, end)), makespan.

### `compute_makespan(solution, instance)`
Compute only the makespan (shortcut via decode_solution).

### `get_neighbor(solution)`
Generate a neighbor by swapping two adjacent elements that belong to different jobs.

### `plot_gantt(solution, instance, title)`
Plot a Gantt chart of the schedule.

---

## sa.py

### `simulated_annealing(instance, T_start, T_min, alpha, max_iter, seed)`
Simulated Annealing for Job Shop Scheduling.

How it works:
1. Start with a random solution
2. At each temperature, try max_iter random neighbors
3. Accept better neighbors always; accept worse with probability e^(-delta/T)
4. Gradually cool: T = alpha * T
5. Return best solution found

Args:
- instance: dict with 'num_jobs', 'num_machines', 'jobs'
- T_start (200): initial temperature (high = more exploration)
- T_min (0.01): stop when T drops below this
- alpha (0.997): cooling rate (close to 1 = slow cooling = better results)
- max_iter (1000): iterations per temperature step
- seed: random seed for reproducibility

Returns: best_solution, best_makespan, history

---

## es.py

### `mutate(solution, strength)`
Create a mutated copy by applying 'strength' successive neighbor swaps.
strength=1 → small change, strength=10 → large change.

### `evolution_strategy(instance, mu, lam, generations, initial_strength, seed)`
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
- instance: dict with 'num_jobs', 'num_machines', 'jobs'
- mu (15): number of parents (selected survivors)
- lam (50): number of offspring per generation (λ)
- generations (3000): number of generations
- initial_strength (5): starting mutation strength (number of swaps)
- seed: random seed for reproducibility

Returns: best_solution, best_makespan, history
