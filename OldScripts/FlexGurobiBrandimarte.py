import gurobipy as gp
from gurobipy import GRB
import collections
import time

def parse_fjsp_dataset(dataset):
    lines = dataset.strip().split("\n")
    num_jobs, num_machines, _ = map(int, lines[0].split())
    jobs_data = []
    
    for i in range(1, len(lines)):
        row = list(map(int, lines[i].split()))
        num_operations = row[0]
        operations = []
        idx = 1
        for op in range(num_operations):
            num_machines_for_op = row[idx]
            machine_options = []
            idx += 1
            for m in range(num_machines_for_op):
                machine, processing_time = row[idx], row[idx + 1]
                machine_options.append((machine - 1, processing_time))  # Machine indices start at 0
                idx += 2
            operations.append(machine_options)
        jobs_data.append(operations)
    
    return jobs_data, num_jobs, num_machines

def main() -> None:
    dataset = """
    10 6 2
    6  2 1 5 3 4 3 5 3 3 5 2 1 2 3 4 6 2 3 6 5 2 6 1 1 1 3 1 3 6 6 3 6 4 3  
    5  1 2 6 1 3 1 1 1 2 2 2 6 4 6 3 6 5 2 6 1 1 
    5  1 2 6 2 3 4 6 2 3 6 5 2 6 1 1 3 3 4 2 6 6 6 2 1 1 5 5 
    5  3 6 5 2 6 1 1 1 2 6 1 3 1 3 5 3 3 5 2 1 2 3 4 6 2
    6  3 5 3 3 5 2 1 3 6 5 2 6 1 1 1 2 6 2 1 5 3 4 2 2 6 4 6 3 3 4 2 6 6 6
    6  2 3 4 6 2 1 1 2 3 3 4 2 6 6 6 1 2 6 3 6 5 2 6 1 1 2 1 3 4 2
    5  1 6 1 2 1 3 4 2 3 3 4 2 6 6 6 3 2 6 5 1 1 6 1 3 1
    5  2 3 4 6 2 3 3 4 2 6 6 6 3 6 5 2 6 1 1 1 2 6 2 2 6 4 6
    6  1 6 1 2 1 1 5 5 3 6 6 3 6 4 3 1 1 2 3 3 4 2 6 6 6 2 2 6 4 6
    6  2 3 4 6 2 3 3 4 2 6 6 6 3 5 3 3 5 2 1 1 6 1 2 2 6 4 6 2 1 3 4 2
    """

    # Parse the dataset
    jobs_data, num_jobs, num_machines = parse_fjsp_dataset(dataset)

    # Start the timer to measure the time taken to solve the problem
    start_time = time.time()

    # Create the model
    model = gp.Model("flexible_job_shop_scheduling")

    # Named tuple to store information about created variables
    task_type = collections.namedtuple("task_type", "start end assign")
    all_tasks = {}

    horizon = sum(min(p for m, p in task) for job in jobs_data for task in job)

    # Create variables and add them to the model
    for job_id, job in enumerate(jobs_data):
        for task_id, task in enumerate(job):
            suffix = f"_{job_id}_{task_id}"
            start_vars = {}
            end_vars = {}
            assign_vars = {}

            for machine, duration in task:
                start_var = model.addVar(vtype=GRB.INTEGER, name=f"start{suffix}_m{machine}")
                end_var = model.addVar(vtype=GRB.INTEGER, name=f"end{suffix}_m{machine}")
                assign_var = model.addVar(vtype=GRB.BINARY, name=f"assign{suffix}_m{machine}")
                start_vars[machine] = start_var
                end_vars[machine] = end_var
                assign_vars[machine] = assign_var

                # Constraint: end = start + duration for the machine if assigned
                model.addConstr(end_var == start_var + duration)

            all_tasks[job_id, task_id] = task_type(start=start_vars, end=end_vars, assign=assign_vars)

            # Each task must be assigned to exactly one machine
            model.addConstr(gp.quicksum(assign_vars[machine] for machine in assign_vars) == 1)

    # Add disjunctive constraints to avoid overlap on the same machine
    for machine in range(num_machines):
        machine_tasks = [
            (job_id, task_id)
            for job_id, job in enumerate(jobs_data)
            for task_id, task in enumerate(job)
            if machine in all_tasks[job_id, task_id].assign
        ]
        for i in range(len(machine_tasks)):
            for j in range(i + 1, len(machine_tasks)):
                job_i, task_i = machine_tasks[i]
                job_j, task_j = machine_tasks[j]

                # Check if both tasks have machine as an option
                if machine in all_tasks[job_i, task_i].assign and machine in all_tasks[job_j, task_j].assign:
                    # Binary variable for disjunction (which task comes first)
                    bin_var = model.addVar(vtype=GRB.BINARY)

                    model.addConstr(
                        all_tasks[job_i, task_i].end[machine] <= all_tasks[job_j, task_j].start[machine] + (1 - bin_var) * horizon,
                        f"disjunctive_{job_i}_{task_i}_{job_j}_{task_j}_1"
                    )
                    model.addConstr(
                        all_tasks[job_j, task_j].end[machine] <= all_tasks[job_i, task_i].start[machine] + bin_var * horizon,
                        f"disjunctive_{job_j}_{task_j}_{job_i}_{task_i}_2"
                    )

    # Add precedence constraints within the same job
    for job_id, job in enumerate(jobs_data):
        for task_id in range(len(job) - 1):
            model.addConstr(
                gp.quicksum(all_tasks[job_id, task_id + 1].start[m] for m in all_tasks[job_id, task_id + 1].start)
                >= gp.quicksum(all_tasks[job_id, task_id].end[m] for m in all_tasks[job_id, task_id].end),
                f"precedence_{job_id}_{task_id}"
            )

    # Objective: minimize makespan (maximum end time across all jobs)
    makespan = model.addVar(vtype=GRB.INTEGER, name="makespan")
    for job_id, job in enumerate(jobs_data):
        last_task = len(job) - 1
        model.addConstr(
            makespan >= gp.quicksum(all_tasks[job_id, last_task].end[m] for m in all_tasks[job_id, last_task].end),
            f"makespan_constraint_{job_id}"
        )
    model.setObjective(makespan, GRB.MINIMIZE)

    # Optimize model
    model.optimize()

    # Display the results
    if model.status == GRB.OPTIMAL:
        print(f"Optimal Schedule Length: {makespan.X}")
        for machine in range(num_machines):
            assigned_jobs = []
            for job_id, job in enumerate(jobs_data):
                for task_id, task in enumerate(job):
                    for m in all_tasks[job_id, task_id].assign:
                        if all_tasks[job_id, task_id].assign[m].X > 0.5:  # Task assigned to this machine
                            start_time = all_tasks[job_id, task_id].start[m].X
                            duration = jobs_data[job_id][task_id][0][1]  # Get the duration for this machine
                            assigned_jobs.append((start_time, f"job_{job_id}_task_{task_id}", duration))
            assigned_jobs.sort()
            print(f"Machine {machine}: {assigned_jobs}")
    else:
        print("No solution found.")

    # Print statistics
    print("\nStatistics")
    print(f"  - Number of variables: {model.NumVars}")
    print(f"  - Number of constraints: {model.NumConstrs}")
    print(f"  - Time taken to solve the problem: {time.time() - start_time}s")

if __name__ == "__main__":
    main()
