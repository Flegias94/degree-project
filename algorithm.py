
from ortools.sat.python import cp_model


groups = ["IE 1", "IE 2"]
courses = ["Math", "Physics", "Chemistry"]
time_slots = list(range(8))
rooms_labels = ["A", "B"]
rooms_indices = list(range(len(rooms_labels)))

model = cp_model.CpModel()

assignments = {}

for g in groups:
    for c in courses:
        t = model.NewIntVar(0, len(time_slots) - 1, f"{g}_{c}_timeslot" )
        r=  model.NewIntVar(0, len(rooms_labels) - 1, f"{g}_{c}_room" )
        assignments[(g,c)] = (t,r)

#constraints

for g in groups:
    for i in range(len(courses)):
        for j in range(i + 1, len(courses)):
            ci = courses[i]
            cj = courses[j]
            ti, _ = assignments[(g, ci)]
            tj, _ = assignments[(g, cj)]
            model.Add(ti != tj)  # group can't have two courses at same time


# Prevent two different group-course pairs from sharing the same room at the same time
for t in time_slots:
    for r in rooms_indices:
        usages = []
        for g in groups:
            for c in courses:
                var_t, var_r = assignments[(g, c)]

                b = model.NewBoolVar(f"{g}_{c}_at_{t}_{r}")
                model.Add(var_t == t).OnlyEnforceIf(b)
                model.Add(var_t != t).OnlyEnforceIf(b.Not())
                model.Add(var_r == r).OnlyEnforceIf(b)
                model.Add(var_r != r).OnlyEnforceIf(b.Not())

                usages.append(b)

        model.Add(sum(usages) <= 1)  # Only one course can use (t, r)

print(f"Total variables: {len(model.Proto().variables)}")
print(f"Total constraints: {len(model.Proto().constraints)}")
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
    for g in groups:
        print(f"\nGroup {g}:")
        for c in courses:
            t, r = assignments[(g, c)]
            room_name = rooms_labels[solver.Value(r)]
            print(f"  {c}: Time Slot {solver.Value(t)}, Room {room_name}")
else:
    print("No valid schedule found.")