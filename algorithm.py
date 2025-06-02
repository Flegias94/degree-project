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

    # Step 4: Timeslot IntVar per session (used for idle time optimization)
    session_times = {}  # session_idx -> IntVar

    for s_idx in range(len(sessions)):
        var = model.NewIntVar(0, len(timeslots) - 1, f"start_time_s{s_idx}")
        session_times[s_idx] = var

        # Link the start time to the assigned timeslot
        model.Add(sum([assignment[key] * key[2] for key in assignment if key[0] == s_idx]) == var)

    # Step 5: Group sessions by semigroup
    semigroup_sessions = defaultdict(list)

    for s_idx, session in enumerate(sessions):
        if session.sgr:
            for sgr in session.sgr.split(", "):  # handle "sgr:1, sgr:2"
                semigroup_sessions[sgr].append(s_idx)

    # Step 6: Define gap variables and minimize total gap
    gap_vars = []

    for sgr, s_indices in semigroup_sessions.items():
        if len(s_indices) > 1:
            max_gap = model.NewIntVar(0, len(timeslots), f"max_gap_{sgr}")
            gaps = []
            for i in range(len(s_indices)):
                for j in range(i + 1, len(s_indices)):
                    si = session_times[s_indices[i]]
                    sj = session_times[s_indices[j]]
                    gap = model.NewIntVar(0, len(timeslots), f"gap_{s_indices[i]}_{s_indices[j]}")
                    model.AddAbsEquality(gap, si - sj)
                    gaps.append(gap)
            model.AddMaxEquality(max_gap, gaps)
            gap_vars.append(max_gap)

    solver.parameters.max_time_in_seconds = 30.0
    solver.parameters.num_search_workers = 8
    # Step 7: Minimize total idle time
    model.Minimize(sum(gap_vars))

    # Solve
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        for (s_idx, r_idx, t_idx), var in assignment.items():
            if solver.Value(var) == 1:
                print(f"{sessions[s_idx].name} -> {rooms[r_idx].sala} @ {timeslots[t_idx]}")
    else:
        print("No feasible schedule found.")
