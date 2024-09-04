import gurobipy as gp
from gurobipy import GRB
import itertools

# ------- DATA -------#

NbHouses = 5

WorkerNames = ["Joe", "Jim"]

TaskNames = [
    "masonry",
    "carpentry",
    "plumbing",
    "ceiling",
    "roofing",
    "painting",
    "windows",
    "facade",
    "garden",
    "moving",
]

Duration = [35, 15, 40, 15, 5, 10, 5, 10, 5, 5]

Worker = {
    "masonry": "Joe",
    "carpentry": "Joe",
    "plumbing": "Jim",
    "ceiling": "Jim",
    "roofing": "Joe",
    "painting": "Jim",
    "windows": "Jim",
    "facade": "Joe",
    "garden": "Joe",
    "moving": "Jim",
}

ReleaseDate = [0, 0, 151, 59, 243]
DueDate = [120, 212, 304, 181, 425]
Weight = [100, 100, 100, 200, 100]

Precedences = [
    ("masonry", "carpentry"),
    ("masonry", "plumbing"),
    ("masonry", "ceiling"),
    ("carpentry", "roofing"),
    ("ceiling", "painting"),
    ("roofing", "windows"),
    ("roofing", "facade"),
    ("plumbing", "facade"),
    ("roofing", "garden"),
    ("plumbing", "garden"),
    ("windows", "moving"),
    ("facade", "moving"),
    ("garden", "moving"),
    ("painting", "moving"),
]

Houses = range(NbHouses)

# -----------------------#


model = gp.Model("")

# for each house, create start and end decision variable
dv_house = {}
max_dueDate = max(DueDate)
for i in Houses:
    dv_house[i] = (
        model.addVar(lb=ReleaseDate[i], ub=max_dueDate, name="start_" + str(i)),
        model.addVar(lb=ReleaseDate[i], ub=max_dueDate, name="end_" + str(i)),
    )

# for each house, create task's start and end decision variables
# since we know the duration of each task,
# add a constraint : task_end - task_start = duration

TaskNames_ids = {}
itvs = {}
for h in Houses:
    for i, t in enumerate(TaskNames):
        _name = str(h) + "_" + str(t)
        itvs[(h, t)] = (
            model.addVar(lb=0, ub=max_dueDate, name="start_" + _name),
            model.addVar(lb=0, ub=max_dueDate, name="end_" + _name),
        )
        model.addConstr(itvs[(h, t)][1] - itvs[(h, t)][0] == Duration[i])
        TaskNames_ids[_name] = i

# ensure that tasks respect the precedences declared earlier
for h in Houses:
    for p in Precedences:
        model.addConstr(itvs[(h, p[1])][0] >= itvs[(h, p[0])][1])

# all tasks executed for a house should be within the confines
# of house start and end decision variable
for h in Houses:
    model.addGenConstrMin(dv_house[h][0], [itvs[(h, t)][0] for t in TaskNames])
    model.addGenConstrMax(dv_house[h][1], [itvs[(h, t)][1] for t in TaskNames])

# identify for each worker what tasks he/she is designated to perform
# for all houses
workers = {}
for w in WorkerNames:
    # workers[w] = [itvs[(h, t)] for h in Houses for t in TaskNames if Worker[t] == w]
    workers[w] = {
        (h, t): itvs[(h, t)] for h in Houses for t in TaskNames if Worker[t] == w
    }

# each worker while making a move from one house to another
# should adhere to transition time
# the transition time between task_house_1 and task_house_2 (say) is amount of time that must elapse
# between the end of task_house_1 and the beginning of task_house_2.
transitionTimes = {}
for i in Houses:
    for j in Houses:
        transitionTimes[i, j] = (i, j, int(abs(i - j)))


# add no overlap constraint
# a worker cannot perform 2 tasks at the same time - same or different house
for w in WorkerNames:
    lst = list(itertools.combinations(workers[w].keys(), 2))
    no_overlap_binary = model.addVars(len(lst), vtype="B")
    for m, n in enumerate(lst):
        one = workers[w][n[0]]
        two = workers[w][n[1]]
        transition_time = transitionTimes[n[0][0], n[1][0]][2]

        model.addGenConstrIndicator(
            no_overlap_binary[m], 1, two[0] >= one[1] + transition_time
        )
        model.addGenConstrIndicator(
            no_overlap_binary[m], 0, two[1] + transition_time <= one[0]
        )


# sequence constraint
# workers_house_tasks = {}
# for w in WorkerNames:
#     for h in Houses:
#         for t in TaskNames:
#             if Worker[t] == w:
#                 workers_house_tasks[(w, h, t)] = itvs[(h, t)]
#     if w == "Joe":
#         task_orders_1 = ["masonry", "carpentry", "roofing", "facade", "garden"]
#         task_orders_2 = ["masonry", "carpentry", "roofing", "garden", "facade"]


# for each house calculate the time for completion
duration_house = {}
for h in Houses:
    duration_house[h] = model.addVar(lb=0, ub=max_dueDate)
    model.addConstr(duration_house[h] == dv_house[h][1] - dv_house[h][0])

# calculate number of days (if any) by which each house
# was completed post the due date
diff_house_end_date_due_date = {}
max_zero_house_end_date_due_date = {}
for h in Houses:
    diff_house_end_date_due_date[h] = model.addVar(lb=0, ub=max_dueDate)
    max_zero_house_end_date_due_date[h] = model.addVar(lb=0, ub=max_dueDate)

    model.addConstr(diff_house_end_date_due_date[h] == dv_house[h][1] - DueDate[h])
    model.addGenConstrMax(
        max_zero_house_end_date_due_date[h], [0, diff_house_end_date_due_date[h]]
    )


model.setObjective(
    gp.quicksum(
        (Weight[h] * max_zero_house_end_date_due_date[h]) + duration_house[h]
        for h in Houses
    ),
    sense=GRB.MINIMIZE,
)

model.optimize()