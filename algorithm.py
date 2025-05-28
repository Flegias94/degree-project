from ortools.sat.python import cp_model
from pprint import pprint
from entity import *
from typing import Dict, List

def allocate(students_group: StudentsGroup, subject_group: SubjectGroup, rooms_group: RoomGroups) -> Dict[str, list[str]]:
    af1_students = students_group.get_for_year_name("AF", 1)
    af1_subjects = subject_group.get_for_students("AF 1")

    af1_subject_sessions = [
        session
        for subject in af1_subjects
        for session in subject.get_sessions(af1_students)
    ]

    for session in af1_subject_sessions:
        for room_type in ('curs', 'seminar', 'laborator'):
            for room in rooms_group.get_rooms_for_type(room_type):
                if session.type == room_type:
                    successful = room.allocate(session)
                    if successful:
                        break

    af1_subjects_names = [session.render() for session in af1_subject_sessions]

    return {"Monday": af1_subjects_names[:6]}  # This is still stubbed — later you'll expand to all days

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
