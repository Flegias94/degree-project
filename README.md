# Degree Project – University Timetabling Tool

This project implements a scheduling tool that generates conflict-free weekly timetables for university students.  
It uses Python to parse structured JSON inputs (students, subjects, rooms), applies a scheduling algorithm, and produces both console output and optional timetable plots.

---

## Features
- Deterministic algorithm for assigning sessions without overlap
- JSON input for easy customization of students, subjects, and rooms
- Visualization of generated timetable using Matplotlib
- Extensible design for adding new constraints or scoring rules

---

## Repository structure

algorithm.py # core scheduler
entity.py # data models
main.py # entry point
plot_schedule.py # timetable plotter
rooms.json # sample rooms
students.json # sample groups
subjects.json # sample sessions
algo.txt # algorithm notes


---

## Quickstart
```bash
# Clone the repository
git clone https://github.com/Flegias94/degree-project.git
cd degree-project

# Install dependencies
pip install -r requirements.txt   # or: pip install matplotlib

# Run the scheduler
python main.py

# Plot the generated timetable
python plot_schedule.py
```

Results

Console output: assigned sessions per timeslot.

Visualization: plot_schedule.py saves a timetable figure.
(Consider adding a sample screenshot here for clarity.)

Roadmap

- Export timetables to CSV/Excel
- Add teacher availability constraints
- Implement scoring system for timetable quality
- Support multiple faculties in one run

Requirements:
- matplotlib>=3.7

Citation
If you use this project for academic purposes, please cite it as:
Siminiceanu Tudor, "University Timetabling Tool", GitHub repository, 2025.

