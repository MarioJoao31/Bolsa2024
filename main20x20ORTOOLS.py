"""Minimal jobshop example."""
import collections
from ortools.sat.python import cp_model
import time


def main() -> None:
    #starts the timer to measure the time taken to solve the problem
    inicio = time.time()
    
    """Minimal jobshop problem."""
    # Data.
    jobs_data = [
        [(0, 29), (1, 9), (2, 49), (3, 62), (4, 44)],
        [(0, 43), (1, 75), (3, 69), (2, 46), (4, 72)],
        [(1, 91), (0, 39), (2, 90), (4, 12), (3, 45)],
        [(1, 81), (0, 71), (4, 9), (2, 85), (3, 22)],
        [(2, 14), (1, 22), (0, 26), (3, 21), (4, 72)],
        [(2, 84), (1, 52), (4, 48), (0, 47), (3, 6)],
        [(1, 46), (0, 61), (2, 32), (3, 32), (4, 30)],
        [(2, 31), (1, 46), (0, 32), (3, 19), (4, 36)],
        [(0, 76), (3, 76), (2, 85), (1, 40), (4, 26)],
        [(1, 85), (2, 61), (0, 64), (3, 47), (4, 90)],
        [(1, 78), (3, 36), (0, 11), (4, 56), (2, 21)],
        [(2, 90), (0, 11), (1, 28), (3, 46), (4, 30)],
        [(0, 85), (2, 74), (1, 10), (3, 89), (4, 33)],
        [(2, 95), (0, 99), (1, 52), (3, 98), (4, 43)],
        [(0, 6), (1, 61), (4, 69), (2, 49), (3, 53)],
        [(1, 2), (0, 95), (3, 72), (4, 65), (2, 25)],
        [(0, 37), (2, 13), (1, 21), (3, 89), (4, 55)],
        [(0, 86), (1, 74), (4, 88), (2, 48), (3, 79)],
        [(1, 69), (2, 51), (0, 11), (3, 89), (4, 74)],
        [(0, 13), (1, 7), (2, 76), (3, 52), (4, 45)],
    ]

    machines_count = 1 + max(task[0] for job in jobs_data for task in job)
    all_machines = range(machines_count)
    # Computes horizon dynamically as the sum of all durations.
    horizon = sum(task[1] for job in jobs_data for task in job)

    # Create the model.
    model = cp_model.CpModel()

    # Named tuple to store information about created variables.
    task_type = collections.namedtuple("task_type", "start end interval")
    # Named tuple to manipulate solution information.
    assigned_task_type = collections.namedtuple(
        "assigned_task_type", "start job index duration"
    )

    # Creates job intervals and add to the corresponding machine lists.
    all_tasks = {}
    machine_to_intervals = collections.defaultdict(list)

    for job_id, job in enumerate(jobs_data):
        for task_id, task in enumerate(job):
            machine, duration = task
            suffix = f"_{job_id}_{task_id}"
            start_var = model.new_int_var(0, horizon, "start" + suffix)
            end_var = model.new_int_var(0, horizon, "end" + suffix)
            interval_var = model.new_interval_var(
                start_var, duration, end_var, "interval" + suffix
            )
            all_tasks[job_id, task_id] = task_type(
                start=start_var, end=end_var, interval=interval_var
            )
            machine_to_intervals[machine].append(interval_var)

    # Create and add disjunctive constraints.
    for machine in all_machines:
        model.add_no_overlap(machine_to_intervals[machine])

    # Precedences inside a job.
    for job_id, job in enumerate(jobs_data):
        for task_id in range(len(job) - 1):
            model.add(
                all_tasks[job_id, task_id + 1].start >= all_tasks[job_id, task_id].end
            )

    # Makespan objective.
    obj_var = model.new_int_var(0, horizon, "makespan")
    model.add_max_equality(
        obj_var,
        [all_tasks[job_id, len(job) - 1].end for job_id, job in enumerate(jobs_data)],
    )
    model.minimize(obj_var)

    # Creates the solver and solve.
    solver = cp_model.CpSolver()
    status = solver.solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print("Solution:")
        # Create one list of assigned tasks per machine.
        assigned_jobs = collections.defaultdict(list)
        for job_id, job in enumerate(jobs_data):
            for task_id, task in enumerate(job):
                machine = task[0]
                assigned_jobs[machine].append(
                    assigned_task_type(
                        start=solver.value(all_tasks[job_id, task_id].start),
                        job=job_id,
                        index=task_id,
                        duration=task[1],
                    )
                )

        # Create per machine output lines.
        output = ""
        for machine in all_machines:
            # Sort by starting time.
            assigned_jobs[machine].sort()
            sol_line_tasks = "Machine " + str(machine) + ": "
            sol_line = "           "

            for assigned_task in assigned_jobs[machine]:
                name = f"job_{assigned_task.job}_task_{assigned_task.index}"
                # add spaces to output to align columns.
                sol_line_tasks += f"{name:15}"

                start = assigned_task.start
                duration = assigned_task.duration
                sol_tmp = f"[{start},{start + duration}]"
                # add spaces to output to align columns.
                sol_line += f"{sol_tmp:15}"

            sol_line += "\n"
            sol_line_tasks += "\n"
            output += sol_line_tasks
            output += sol_line

        # Finally print the solution found.
        print(f"Optimal Schedule Length: {solver.objective_value}")
        print(output)
    else:
        print("No solution found.")

    # Statistics.
    print("\nStatistics")
    print(f"  - conflicts: {solver.num_conflicts}")
    print(f"  - branches : {solver.num_branches}")
    print(f"  - wall time: {solver.wall_time}s")
    print(f"  - time taken to solve the problem: {time.time()-inicio}s")

if __name__ == "__main__":
    main()