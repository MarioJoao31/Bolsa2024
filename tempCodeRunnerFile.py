import gurobipy as gp
from gurobipy import GRB
import collections
import time

def main() -> None:
    # Start the timer to measure the time taken to solve the problem
    inicio = time.time()

    # Data
    jobs_data = [
       [(8, 35), (2, 78), (7, 79), (14, 65), (12, 53), (0, 14), (4, 93), (3, 70), (13, 14), (5, 90), (9, 95), (10, 49), (6, 36), (1, 85), (11, 1)],
[(2, 83), (8, 41), (6, 22), (4, 29), (11, 52), (0, 71), (9, 16), (7, 93), (5, 54), (3, 63), (1, 12), (10, 85), (13, 62), (14, 45), (12, 30)],
[(5, 60), (11, 43), (8, 71), (14, 2), (12, 50), (1, 37), (4, 86), (9, 81), (10, 60), (6, 57), (13, 66), (0, 24), (2, 98), (3, 92), (7, 69)],
[(9, 14), (13, 59), (8, 35), (6, 6), (12, 25), (5, 57), (10, 1), (2, 44), (1, 94), (0, 30), (14, 95), (11, 93), (3, 51), (4, 52), (7, 16)],
[(8, 96), (10, 39), (3, 75), (13, 98), (14, 2), (5, 38), (4, 69), (0, 32), (12, 95), (11, 63), (9, 4), (6, 11), (2, 50), (1, 95), (7, 78)],
[(7, 73), (2, 28), (9, 43), (5, 47), (10, 57), (4, 88), (3, 33), (1, 13), (11, 7), (8, 49), (6, 23), (14, 38), (13, 21), (0, 99), (12, 72)],
[(2, 3), (10, 80), (1, 67), (12, 93), (14, 91), (3, 31), (0, 52), (4, 64), (9, 83), (5, 2), (11, 90), (13, 64), (7, 16), (8, 18), (6, 25)],
[(13, 23), (6, 30), (11, 22), (12, 54), (8, 68), (7, 63), (14, 89), (5, 95), (3, 5), (4, 37), (0, 5), (10, 42), (2, 17), (1, 54), (9, 46)],
[(8, 44), (4, 59), (6, 87), (7, 62), (0, 51), (11, 55), (13, 3), (12, 40), (2, 26), (3, 18), (10, 15), (1, 18), (5, 72), (14, 35), (9, 60)],
[(2, 27), (6, 14), (12, 77), (9, 24), (8, 55), (11, 67), (1, 59), (3, 19), (13, 29), (4, 33), (10, 88), (5, 30), (0, 91), (7, 11), (14, 11)],
[(0, 67), (9, 94), (4, 50), (8, 2), (10, 83), (2, 19), (11, 29), (12, 37), (14, 58), (6, 32), (3, 38), (7, 99), (5, 88), (1, 49), (13, 70)],
[(8, 60), (1, 7), (12, 81), (5, 82), (7, 58), (10, 83), (9, 16), (4, 1), (11, 69), (6, 7), (13, 3), (2, 84), (14, 8), (0, 12), (3, 93)],
[(13, 92), (14, 81), (2, 4), (9, 78), (7, 9), (8, 78), (12, 75), (4, 5), (10, 50), (6, 8), (1, 44), (0, 4), (5, 60), (11, 94), (3, 74)],
[(1, 32), (0, 88), (12, 31), (2, 68), (13, 31), (8, 10), (3, 45), (14, 75), (4, 82), (7, 51), (6, 55), (9, 99), (11, 44), (10, 84), (5, 22)],
[(3, 12), (13, 35), (2, 64), (5, 17), (9, 42), (6, 46), (7, 65), (4, 74), (8, 96), (0, 28), (12, 86), (10, 95), (14, 93), (1, 67), (11, 56)]

    ]

    machines_count = 1 + max(task[0] for job in jobs_data for task in job)
    horizon = sum(task[1] for job in jobs_data for task in job)

    # Create the model
    model = gp.Model("job_shop_scheduling")

    # Named tuple to store information about created variables
    task_type = collections.namedtuple("task_type", "start end")
    all_tasks = {}

    # Create variables and add them to the model
    for job_id, job in enumerate(jobs_data):
        for task_id, (machine, duration) in enumerate(job):
            suffix = f"_{job_id}_{task_id}"
            start_var = model.addVar(vtype=GRB.INTEGER, name=f"start{suffix}")
            end_var = model.addVar(vtype=GRB.INTEGER, name=f"end{suffix}")
            all_tasks[job_id, task_id] = task_type(start=start_var, end=end_var)

            # Add constraint to ensure end = start + duration
            model.addConstr(end_var == start_var + duration, f"duration{suffix}")

    # Add disjunctive constraints to avoid overlap on the same machine
    for machine in range(machines_count):
        machine_tasks = [
            (job_id, task_id)
            for job_id, job in enumerate(jobs_data)
            for task_id, task in enumerate(job)
            if task[0] == machine
        ]
        for i in range(len(machine_tasks)):
            for j in range(i + 1, len(machine_tasks)):
                job_i, task_i = machine_tasks[i]
                job_j, task_j = machine_tasks[j]

                # Binary variable for disjunction
                bin_var = model.addVar(vtype=GRB.BINARY)

                model.addConstr(
                    all_tasks[job_i, task_i].end <= all_tasks[job_j, task_j].start + (1 - bin_var) * horizon,
                    f"disjunctive_{job_i}_{task_i}_{job_j}_{task_j}_1"
                )
                model.addConstr(
                    all_tasks[job_j, task_j].end <= all_tasks[job_i, task_i].start + bin_var * horizon,
                    f"disjunctive_{job_j}_{task_j}_{job_i}_{task_i}_2"
                )

    # Add precedence constraints within the same job
    for job_id, job in enumerate(jobs_data):
        for task_id in range(len(job) - 1):
            model.addConstr(
                all_tasks[job_id, task_id + 1].start >= all_tasks[job_id, task_id].end,
                f"precedence_{job_id}_{task_id}",
            )

    # Objective: minimize makespan (maximum end time across all jobs)
    makespan = model.addVar(vtype=GRB.INTEGER, name="makespan")
    for job_id, job in enumerate(jobs_data):
        model.addConstr(
            makespan >= all_tasks[job_id, len(job) - 1].end,
            f"makespan_constraint_{job_id}",
        )
    model.setObjective(makespan, GRB.MINIMIZE)

    # Optimize model
    model.optimize()

    # Display the results
    if model.status == GRB.OPTIMAL:
        print(f"Optimal Schedule Length: {makespan.X}")
        output = ""
        for machine in range(machines_count):
            assigned_jobs = []
            for job_id, job in enumerate(jobs_data):
                for task_id, (task_machine, _) in enumerate(job):
                    if task_machine == machine:
                        start_time = all_tasks[job_id, task_id].start.X
                        duration = jobs_data[job_id][task_id][1]
                        assigned_jobs.append((start_time, f"job_{job_id}_task_{task_id}", duration))
            assigned_jobs.sort()
            sol_line_tasks = f"Machine {machine}: "
            sol_line = "           "
            for start_time, name, duration in assigned_jobs:
                sol_line_tasks += f"{name:15}"
                sol_tmp = f"[{int(start_time)},{int(start_time + duration)}]"
                sol_line += f"{sol_tmp:15}"
            sol_line += "\n"
            sol_line_tasks += "\n"
            output += sol_line_tasks
            output += sol_line

        print(output)
    else:
        print("No solution found.")

    # Print statistics
    print("\nStatistics")
    print(f"  - Number of variables: {model.NumVars}")
    print(f"  - Number of constraints: {model.NumConstrs}")
    print(f"  - Time taken to solve the problem: {time.time() - inicio}s")

if __name__ == "__main__":
    main()
