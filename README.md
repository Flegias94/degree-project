# Degree Project — University Timetabling (Python)

End-to-end timetabling tool that reads input data from JSON (students, subjects, rooms), builds a feasible weekly schedule, and optionally renders a visual timetable.

## Highlights
- Input as simple JSON files (editable with any text editor).
- Deterministic scheduling algorithm with clear constraints (no overlaps for groups/rooms/teachers, room capacity respected).
- CLI style: run the scheduler, then render a plot of the result.
- Small, readable codebase for review.

Repository structure

## Repository structure


algorithm.py # core scheduler
entity.py # data models
main.py # entry point
plot_schedule.py # timetable plotter
rooms.json # sample rooms
students.json # sample groups
subjects.json # sample sessions
algo.txt # algorithm notes

*(Files as seen in the repo listing.)*
Quickstart (commands)
## Quickstart
1) **Clone**
```bash
git clone https://github.com/Flegias94/degree-project.git
cd degree-project
pip install -r requirements.txt  # or: pip install matplotlib
python main.py
python plot_schedule.py

Python

Python 3.10+ recommended.

If needed, install matplotlib:

pip install matplotlib

Run scheduler
python main.py
This reads rooms.json, students.json, subjects.json, runs the algorithm, and prints/saves the schedule (see console/output notes in main.py).

Render timetable
python plot_schedule.py
Produces a figure showing the scheduled sessions.

Data (inputs)
rooms.json: list of rooms with at least an identifier and capacity.
students.json: groups/semigroups or cohorts, each with an identifier and size.
subjects.json: subjects/sessions with group, duration, and required room type if any.
The provided JSON files are examples; adjust to your context. Keep identifiers consistent across files.

Constraints (core)
- A group/teacher cannot attend two sessions at the same time.
- A room hosts at most one session at a time.
- Room capacity must cover assigned group size.
- Sessions respect their specified durations and timeslots.

How it works (overview)
- main.py loads JSON → builds in-memory entities → calls the scheduler in algorithm.py.
- The algorithm searches valid timeslot–room assignments that satisfy hard constraints.
- plot_schedule.py reads the produced schedule structure and plots a weekly grid.

Customizing

- Edit the three JSON files to match your faculty (rooms, cohorts, subjects/sessions).
- Tune timeslots or scoring/ordering rules inside algorithm.py.
- Adjust colors/labels in plot_schedule.py.

Roadmap
Export to CSV/Excel.
Add teacher availability windows.
Add penalty scoring (gaps, early/late slots) and an objective summary.
Unit tests and a simple CLI (--input, --output, --plot).

