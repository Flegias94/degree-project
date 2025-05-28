import json

from dataclasses import dataclass, field
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
    _allocated: int = 0
    _allocated_sessions: list['SubjectSession'] = field(default_factory=list)

    @classmethod
    def from_json(cls, data):
        if "int_start" in data:
            del data["int_start"]
        if "int_stop" in data:
            del data["int_stop"]
        return Room(**data)
    
    def allocate(self, session: 'SubjectSession') -> bool:
        free_slots = self.nr_locuri - self._allocated
        if free_slots >= session.how_many:
            self._allocated += session.how_many
            self._allocated_sessions.append(session)
            session.room = self
            return True
        return False
    
    @property
    def allocated(self):
        return self._allocated_sessions

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
    
    def get_rooms_for_type(self, type_: str):
        rooms: list[Room] = []
        for room in self.rooms:
            if room.scop == type_:
                rooms.append(room)
        return rooms


@dataclass
class SubjectSession:
    name: str
    type: Literal["curs", "laborator", "seminar"]
    how_many: int 
    sgr: str = ''
    room: Room = None

    def render(self):
        if not self.room:
            return f"{self.name}\n{self.type}\n "
        sgr_str = ", ".join(map(lambda n: n.sgr, self.room.allocated))
        return f"{self.name}\n{self.type}\n{sgr_str}\n{self.room.sala}".strip()


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

    def get_sessions(self, students: 'Students') -> list['SubjectSession']:
        sessions = []
        # Curs sessions (whole group)
        for _ in range(self.ore_curs // 2):
            sessions.append(SubjectSession(
                name=self.nume_materie,
                type="curs",
                how_many=students.nr_studenti
            ))

        # Practice sessions for semigroups (seminar/lab)
        semigroups = [f"sgr:{i+1}" for i in range(students.nr_semigrupe)]

        # Pair semigroups (or handle last one if odd number)
        for i in range(0, len(semigroups), 2):
            pair = semigroups[i:i+2]
            group_size = (students.nr_studenti // students.nr_semigrupe) * len(pair)

            for _ in range(self.ore_practice // 2):
                sessions.append(SubjectSession(
                    name=self.nume_materie,
                    type=self.tip_ora,
                    how_many=group_size,
                    sgr=", ".join(pair)
                ))

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
    
@dataclass
class Timeslot:
    day: str
    start_hour: int
    duration: int = 2

    def __str__(self):
        return f"{self.day} {self.start_hour:02d}:00 - {self.start_hour + self.duration:02d}:00"

@dataclass
class RoomAllocation:
    session: SubjectSession
    room: Room
    timeslot: Timeslot

