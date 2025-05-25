import json

from dataclasses import dataclass
from typing import Literal, Sequence


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
    @classmethod
    def load(cls, path: str = "students.json"):
        with open(path, "r") as f:
            raw_data = json.load(f)
        data = cls.from_json(raw_data)
        return data


@dataclass
class Room:
    id: int
    sala: str
    nr_locuri: int
    scop: str

    @classmethod
    def from_json(cls, data):
        if "int_start" in data:
            del data["int_start"]
        if "int_stop" in data:
            del data["int_stop"]
        return Room(**data)
    


@dataclass
class RoomGroups:
    rooms: Sequence[Room]

    @classmethod
    def from_json(cls, data):
        rooms = [Room.from_json(room) for room in data]
        return cls(rooms)
    
    @classmethod
    def load(cls, path: str = "rooms.json"):
        with open(path, "r") as f:
            raw_data = json.load(f)
        data = cls.from_json(raw_data)
        return data


@dataclass
class SubjectSession:
    name: str
    type: Literal["curs", "laborator", "seminar"]
    sgr: str = ''

    def render(self):
        return f"{self.name}\n{self.type}\n{self.sgr}"


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
    
    @classmethod
    def load(cls, path: str = 'subjects.json'):
        with open(path, "r") as f:
            raw_data = json.load(f)
        data = cls.from_json(raw_data)
        return data
   
