from dataclasses import dataclass
import json
from pprint import pprint
from typing import Literal, Sequence
import matplotlib.pyplot as plt
import pandas as pd

@dataclass
class Subject:
    id: int
    nume_specializare_mat: str
    nume_materie: str
    tip_ora: str
    prof_titular: str
    nr_saptamani: int
    ore_curs: int
    ore_practice: int
    prof_asistenti: str

    @classmethod
    def from_json(cls, data):
        return cls(**data)
    
    def get_sessions(self, students: 'Students'):
        sessions = []
        for _ in range(self.ore_curs // 2):
            sessions.append(SubjectSession(self.nume_materie, "curs"))
        for sgr in range(students.nr_semigrupe):
            sgr_name = f"sgr:{sgr+1}"
            for _ in range(self.ore_practice // 2):
                sessions.append(SubjectSession(self.nume_materie, self.tip_ora, sgr_name))
        return sessions

@dataclass
class SubjectGroup:
    subjects: Sequence[Subject]

    @classmethod
    def from_json(cls, data):
        subjects = [Subject.from_json(subject) for subject in data]    
        return cls(subjects)
    
    def get_for_students(self, profile_name: str) -> list[Subject]:
        subjects: list[Subject] = []
        for subject in self.subjects:
            if subject.nume_specializare_mat == profile_name:
                subjects.append(subject)
        return subjects

@dataclass
class SubjectSession:
    name: str
    type: Literal["curs", "laborator", "seminar"]
    sgr: str = ''

    def render(self):
        return f"{self.name}\n{self.type}\n{self.sgr}"
    
@dataclass
class Students:
    id: int
    nume_specializare: str
    nr_studenti: int
    nr_grupe: int
    nr_semigrupe: int
    an_studiu: int

    @classmethod
    def from_json(cls, data):
        return Students(**data)
    
@dataclass
class StudentsGroup:
    students: Sequence[Students]

    @classmethod
    def from_json(cls, data):
        students = [Students.from_json(students) for students in data]
        return cls(students)
    
    def get_for_year_name(self, profile_name: str, year: int) -> Students:
        for students in self.students:
            if students.nume_specializare == profile_name and \
                students.an_studiu == year:   
                return students

def load_subjects():
    with open("subjects.json", "r") as f:
        raw_subjects = json.load(f)
    subjects = SubjectGroup.from_json(raw_subjects)
    return subjects

def load_rooms():
    with open("rooms.json", "r") as f:
        rooms = json.load(f)
    return rooms

def load_students():
    with open("students.json", "r") as f:
        raw_students = json.load(f)
    students = StudentsGroup.from_json(raw_students)
    return students

def main():
    students_group = load_students()
    af1_students = students_group.get_for_year_name("AF", 1)
    subject_group = load_subjects()
    af1_subjects = subject_group.get_for_students("AF 1")
    af1_subject_sessions = [session for subject in af1_subjects for session in subject.get_sessions(af1_students)]
    af1_subjects_names = [session.render() for session in af1_subject_sessions]

        
    pprint(af1_subjects)
    plotting({"Monday": af1_subjects_names[:6]})

def plotting(data: dict[str, list[str]]):

    week_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    time_slots = [f"{hour}:00 - {hour+2}:00" for hour in range(8, 20, 2)]

    schedule_df = pd.DataFrame('', index=time_slots, columns=week_days)

    for day, schedule in data.items():
        for index, subject in enumerate(schedule):
            schedule_df.iloc[index, schedule_df.columns.get_loc(day)] = subject 


    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('off')
    table = ax.table(cellText=schedule_df.values,
                    rowLabels=schedule_df.index,
                    colLabels=schedule_df.columns,
                    cellLoc='center',
                    loc='center')

    table.scale(1, 2)
    plt.title("Weekly Schedule Table", fontweight='bold')
    plt.tight_layout()
    plt.savefig("weekly_schedule.png", dpi=300, bbox_inches="tight")
    plt.show()



if __name__ == "__main__":
    main()
