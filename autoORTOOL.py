import collections
from ortools.sat.python import cp_model
import time
import os

# Path to the dataset folder
folder_path = '/Users/mariopinto/Desktop/Bolsa2024/jssp/taillard/'

# Function to parse the dataset from a file
def parse_dataset(file_path):
    with open(file_path, 'r') as file:
        file_content = file.read()

    lines = file_content.strip().splitlines()
    
    data = []
    for line in lines:
        # Skip comment lines or empty lines
        if line.startswith("#") or line.strip() == "":
            continue
        # Convert the line to a list of integers
        try:
            row = list(map(int, line.split()))
            data.append(row)
        except ValueError:
            print(f"Could not parse line: {line}")
            return []

    # Ignore the first data line which contains the number of machines and jobs
    jobs_data = []
    for job in data[1:]:  # Skip the first data row
        job_tasks = []
        for i in range(0, len(job), 2):
            machine_id = job[i]
            processing_time = job[i + 1]
            job_tasks.append((machine_id, processing_time))
        jobs_data.append(job_tasks)
    
    return jobs_data

# OR-Tools Job Shop Solver function
def solve_jobshop(jobs_data):
    # Start the timer to measure the time taken to solve the problem
    inicio = time.time()

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

    # Creates job intervals and adds them to the corresponding machine lists.
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

    # Creates the solver and solves.
    solver = cp_model.CpSolver()
    status = solver.solve(model)

    output = ""

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        output += "Solution:\n"
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

        # Finally, print the solution found.
        output += f"Optimal Schedule Length: {solver.objective_value}\n"
    else:
        output += "No solution found.\n"

    # Statistics.
    output += "\nStatistics\n"
    output += f"  - conflicts: {solver.num_conflicts}\n"
    output += f"  - branches : {solver.num_branches}\n"
    output += f"  - wall time: {solver.wall_time}s\n"
    output += f"  - time taken to solve the problem: {time.time()-inicio}s\n"

    return output

# Function to automatically solve all dataset files
def process_all_files():
    output_path = "/Users/mariopinto/Desktop/Bolsa2024/output_resultsERTOOLS.txt"

    with open(output_path, "w") as output_file:
        for i in range(1, 11):  # Assuming 10 files (ta01.js to ta10.js)
            file_name = f"ta{i:02d}.jss"
            file_path = os.path.join(folder_path, file_name)
            print(f"Processing file: {file_name}")
            jobs_data = parse_dataset(file_path)

            if jobs_data:
                result = solve_jobshop(jobs_data)
                output_file.write(f"Results for {file_name}:\n")
                output_file.write(result)
                output_file.write("\n" + "="*40 + "\n")
            else:
                output_file.write(f"Error parsing {file_name}\n")
                output_file.write("\n" + "="*40 + "\n")

# Automatically process all files
process_all_files()
