from collections import defaultdict
from ortools.sat.python import cp_model
from pprint import pprint
from entity import *
from typing import Dict, List, Tuple


def solve_schedule(sessions: List[SubjectSession], rooms: List[Room], timeslots: List[Timeslot]):
    model = cp_model.CpModel()

    # Step 1: Build variables
    assignment = {}  # (session_idx, room_idx, timeslot_idx) -> BoolVar

    for s_idx, session in enumerate(sessions):
        for r_idx, room in enumerate(rooms):
            if room.scop != session.type:
                continue  # only rooms of the right type

            if room.nr_locuri < session.how_many:
                continue  # room too small

            for t_idx, timeslot in enumerate(timeslots):
                var = model.NewBoolVar(f"s{s_idx}_r{r_idx}_t{t_idx}")
                assignment[(s_idx, r_idx, t_idx)] = var

    # Step 2: Each session must be assigned exactly once
    for s_idx in range(len(sessions)):
        model.AddExactlyOne([
            assignment[key] for key in assignment if key[0] == s_idx
        ])

    # Step 3: No room conflicts (at most one session per room+timeslot)
    for r_idx in range(len(rooms)):
        for t_idx in range(len(timeslots)):
            model.AddAtMostOne([
                assignment[key] for key in assignment
                if key[1] == r_idx and key[2] == t_idx
            ])

    # Step 4: No semigroup/student overlaps
    # You’ll need a way to extract student groups per session, then prevent overlap

    # Step 5 (Optional): Add scoring objective (e.g., morning vs evening)
    # model.Maximize(...)

    # Solve
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        for (s_idx, r_idx, t_idx), var in assignment.items():
            if solver.Value(var) == 1:
                print(f"{sessions[s_idx].name} -> {rooms[r_idx].sala} @ {timeslots[t_idx]}")
    else:
        print("No feasible schedule found.")
