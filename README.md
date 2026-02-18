# Designing Randomized Optimization Algorithms

## Task

In this assignment, you must develop two algorithms, i.e., one **trajectory-based** and one **population-based**, to solve the **job shop scheduling problem**. The problem, also known as the job-shop problem, involves scheduling a set of jobs on a set of machines, where each job consists of a sequence of operations that must be processed in a specific order (precedence constraints). The goal is typically to find the optimal sequence of jobs on each machine to minimize the **makespan**, i.e., the total time required to complete all jobs.

You can read more about the problem here: [Job Shop Scheduling](https://developers.google.com/optimization/scheduling/job_shop)

### Instances

Choose and work with as many of the benchmark instances as you want. See [jobshop.txt](jobshop.txt) for the available instances.

The instances are formatted with one line per job, listing the machine number and processing time for each step. For example, the following line:

```
4 88 8 68 6 94
```

means that job 1 (first line) should be assigned to machine 4 first, which takes 88 minutes to process; then to machine 8, which takes 68 minutes; and finally to machine 6, which takes 94 minutes.

### Algorithms

Feel free to experiment with as many of the algorithms we saw in the lecture as you want. Keep in mind that you need at least one trajectory-based and one population-based included in the final submission.

> [!TIP]
> A good practice is to modularize your algorithms so you can test several versions without rewriting the code.

## Submission

You must submit a **Jupyter Notebook**, in which:

1. **(a)** You include the algorithms
2. **(b)** Some analysis with visualizations
3. **(c)** Comparative results

Use headers to distinguish each section.

### Algorithms

Include adequate comments in the algorithms.

Any preparatory/preprocessing steps required before running your algorithm(s) should be included before the algorithms section.

### Visualizations

The visualizations should be accompanied by text where you reflect on the plots.

### Results

The comparative results should support your final choice of algorithms.

> [!IMPORTANT]
> Each cell should have been executed when you submit the Notebook.
