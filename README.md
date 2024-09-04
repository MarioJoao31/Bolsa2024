# Jobshop Schedule Problem Comparison

This repository contains scripts for comparing the results and execution time of solving the Jobshop Schedule Problem using OR-Tools and Gurobi.

## Introduction

The Jobshop Schedule Problem is a classic optimization problem in which a set of jobs must be scheduled on a set of machines, subject to various constraints. In this project, we compare the performance of two popular optimization solvers, OR-Tools and Gurobi, in solving this problem.

## Installation

To run the scripts, you need to have the following dependencies installed:

- OR-Tools (version X.X.X)
- Gurobi (version X.X.X)

Please refer to the official documentation of each solver for installation instructions.

## Usage

1. Clone this repository:

   ```
   git clone https://github.com/your-username/your-repo.git
   ```

2. Run the script:

   ```
   python MatrixPickerORTOOLS.py

   OR

   python MatrixPickerGurobi.py

   ```

3. Choose a .jss file with a matrix.

4. The results will appear in the console.

## Results

### Problem Overview

This section presents the results of solving a job shop scheduling problem using two optimization tools: **Gurobi** and **OR-Tools**. The goal is to minimize the makespan, i.e., the total time required to complete all jobs.

### Input Data

Both solvers used the following input data, where each job consists of a sequence of tasks that need to be processed on specific machines for a given duration:

### Gurobi Results

**Optimal Schedule Length:** 55.0

#### Machine Assignments:

- **Machine 0:** job_0_task_1 [8,11], job_3_task_1 [16,21], job_2_task_3 [21,30], job_5_task_3 [30,40], job_1_task_4 [40,50], job_4_task_4 [51,54]
- **Machine 1:** job_1_task_0 [0,8], job_5_task_0 [8,11], job_3_task_0 [11,16], job_0_task_2 [16,22], job_4_task_1 [22,25], job_2_task_4 [30,31]
- **Machine 2:** job_2_task_0 [0,5], job_0_task_0 [7,8], job_1_task_1 [8,13], job_4_task_0 [13,22], job_3_task_2 [22,27], job_5_task_5 [49,50]
- **Machine 3:** job_2_task_1 [5,9], job_5_task_1 [11,14], job_3_task_3 [27,30], job_0_task_3 [36,43], job_1_task_5 [50,54], job_4_task_5 [54,55]
- **Machine 4:** job_1_task_2 [13,23], job_4_task_2 [25,30], job_3_task_4 [30,38], job_2_task_5 [38,45], job_5_task_4 [45,49], job_0_task_5 [49,55]
- **Machine 5:** job_2_task_2 [9,17], job_5_task_2 [17,26], job_1_task_3 [26,36], job_4_task_3 [36,40], job_0_task_4 [43,46], job_3_task_5 [46,55]

#### Statistics:

- **Number of variables:** 163
- **Number of constraints:** 252
- **Time taken to solve:** 0.036775s

### OR-Tools Results

**Optimal Schedule Length:** 55.0

#### Machine Assignments:

- **Machine 0:** job_0_task_1 [6,9], job_3_task_1 [13,18], job_2_task_3 [18,27], job_5_task_3 [28,38], job_1_task_4 [38,48], job_4_task_4 [48,51]
- **Machine 1:** job_1_task_0 [0,8], job_3_task_0 [8,13], job_5_task_0 [13,16], job_0_task_2 [16,22], job_4_task_1 [22,25], job_2_task_4 [27,28]
- **Machine 2:** job_2_task_0 [0,5], job_0_task_0 [5,6], job_1_task_1 [8,13], job_4_task_0 [13,22], job_3_task_2 [22,27], job_5_task_5 [42,43]
- **Machine 3:** job_2_task_1 [5,9], job_5_task_1 [16,19], job_3_task_3 [27,30], job_0_task_3 [30,37], job_1_task_5 [48,52], job_4_task_5 [52,53]
- **Machine 4:** job_1_task_2 [13,23], job_4_task_2 [25,30], job_3_task_4 [30,38], job_5_task_4 [38,42], job_0_task_5 [42,48], job_2_task_5 [48,55]
- **Machine 5:** job_2_task_2 [9,17], job_5_task_2 [19,28], job_1_task_3 [28,38], job_0_task_4 [38,41], job_4_task_3 [41,45], job_3_task_5 [45,54]

#### Statistics:

- **Conflicts:** 2
- **Branches:** 61
- **Wall time:** 0.013268s
- **Time taken to solve:** 0.022327s

## Conclusion

Based on the comparison, we can conclude that...

![Comparison Chart](images/comparison_chart.png)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
