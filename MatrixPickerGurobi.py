import tkinter as tk
from tkinter import filedialog, messagebox
import collections
import gurobipy as gp
from gurobipy import GRB
import time

# Function to parse the dataset from the selected file
def parse_dataset(file_content):
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
            messagebox.showerror("Parsing Error", f"Could not parse line: {line}")
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

# Function to open and read the file
def open_file():
    global jobs_data
    # Open file dialog to select file (including .jss files)
    file_path = filedialog.askopenfilename(
        title="Select the dataset file", 
        filetypes=[ ("Job Shop Scheduling Files", "*.jss"), ("All Files", "*.*")]
    )
    
    if file_path:
        try:
            with open(file_path, 'r') as file:
                file_content = file.read()
                jobs_data = parse_dataset(file_content)
                if not jobs_data:
                    messagebox.showinfo("No Data", "The file was parsed, but no valid data was found.")
                else:
                    print_matrix(jobs_data)
                    solve_jobshop(jobs_data)
        except Exception as e:
            messagebox.showerror("File Error", f"Could not read the file: {str(e)}")

# Function to print the matrix in the console
def print_matrix(jobs_data):
    if jobs_data:
        print("Parsed Matrix:")
        for i, job in enumerate(jobs_data):
            print(f"Job {i}: {job}")
    else:
        print("No valid job data to display.")

# Gurobi Job Shop Solver function
def solve_jobshop(jobs_data):
    # Start the timer to measure the time taken to solve the problem
    inicio = time.time()

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

# Set up the main application window
root = tk.Tk()
root.title("Dataset to Matrix Parser")

# Set the window size
root.geometry("250x150")  # Increase the size of the window

# Create a frame for better layout management
frame = tk.Frame(root)
frame.pack(pady=20)

# Create a button to open the file
open_button = tk.Button(root, text="Open File and solve using Gurobi", padx=20, pady=10, command=open_file)
open_button.pack()

# Run the application
root.mainloop()
