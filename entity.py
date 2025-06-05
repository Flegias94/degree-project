from __future__ import annotations

import json
import math
import textwrap
from dataclasses import dataclass, field
from typing import Dict, List, Literal, Sequence, Set, Tuple


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
        name = '\n'.join(textwrap.wrap(self.name, width=22))
        lines = [name, f"({self.type})"]
        if self.sgr:
            lines.append(f"{self.sgr}")
        if self.room:
            lines.append(self.room.sala)
        return "\n".join(lines)


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

    def get_sessions(self, students: 'Students', available_rooms: List['Room']) -> list['SubjectSession']:
        sessions = []
        # Curs sessions (whole group)
        for _ in range(math.ceil(self.ore_curs / 2)):
            sessions.append(SubjectSession(
                name=self.nume_materie,
                type="curs",
                how_many=students.nr_studenti
            ))

        # Determine groupings for practice/lab/seminar
        semigroups = [f"sgr:{i + 1}" for i in range(students.nr_semigrupe)]
        group_size = students.nr_studenti // students.nr_semigrupe
        pair_size = group_size * 2
        can_use_pairs = any(
            room.scop == self.tip_ora and room.nr_locuri >= pair_size
            for room in available_rooms
        )

        if can_use_pairs:
            # Use semigroup pairs (default)
            for i in range(0, len(semigroups), 2):
                pair = semigroups[i:i + 2]
                size = group_size * len(pair)
                for _ in range(math.ceil(self.ore_practice / 2)):
                    sessions.append(SubjectSession(
                        name=self.nume_materie,
                        type=self.tip_ora,
                        how_many=size,
                        sgr=", ".join(pair)
                    ))
        else:
            # Fallback to individual semigroups
            for sgr in semigroups:
                for _ in range(math.ceil(self.ore_practice / 2)):
                    sessions.append(SubjectSession(
                        name=self.nume_materie,
                        type=self.tip_ora,
                        how_many=group_size,
                        sgr=sgr
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
    rooms: List['Room']
    used_slots: Set[Tuple[int, str, int]] = field(default_factory=set)
    schedule: Dict[str, List['SubjectSession' | str]] = field(init=False)

    def __post_init__(self):
        self.schedule = {
            day: [""] * 6 for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        }

    def allocate(self, sessions: List['SubjectSession']) -> Dict[str, List['SubjectSession' | str]]:
        week_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        hour_blocks = [8, 10, 12, 14, 16, 18]
        scorer = TimeSlotScorer()

        for session in sessions:
            assigned = False

            preferred_slots = [
                (day, hour, scorer.get_score(session.type, hour))
                for day in week_days
                for hour in hour_blocks
            ]
            preferred_slots.sort(key=lambda x: x[2], reverse=True)

            for day, hour, _ in preferred_slots:
                slot_index = hour_blocks.index(hour)

                for room in self.rooms:
                    if (
                            room.scop == session.type and
                            room.nr_locuri >= session.how_many and
                            (room.id, day, hour) not in self.used_slots and
                            self.schedule[day][slot_index] == ""
                    ):
                        session.room = room
                        room._allocated_sessions.append(session)
                        self.used_slots.add((room.id, day, hour))
                        self.schedule[day][slot_index] = session
                        assigned = True
                        break

                if assigned:
                    break

            if not assigned:
                for day in week_days:
                    for slot_index, hour in enumerate(hour_blocks):
                        if self.schedule[day][slot_index] == "":
                            self.schedule[day][slot_index] = f"{session.name} ({session.type}, {session.sgr})"
                            assigned = True
                            break
                    if assigned:
                        break

        return self.schedule


@dataclass
class TimeSlotScorer:
    weights_course: Dict[int, int] = None
    weights_lab: Dict[int, int] = None

    def __post_init__(self):
        if self.weights_course is None:
            self.weights_course = {
                8: 5, 10: 3, 12: 3, 14: 3, 16: 2, 18: 1, 20: 0
            }
        if self.weights_lab is None:
            self.weights_lab = {
                8: 0, 10: 5, 12: 5, 14: 5, 16: 3, 18: 1, 20: 0
            }

    def get_score(self, session_type: Literal["curs", "seminar", "laborator"], hour: int) -> int:
        if session_type == "curs":
            return self.weights_course.get(hour, 0)
        else:
            return self.weights_lab.get(hour, 0)

    def score_timeslots(self, session_type: Literal["curs", "seminar", "laborator"], hours: List[int]) -> List[
        Tuple[int, int]]:
        scored = [(hour, self.get_score(session_type, hour)) for hour in hours]
        return sorted(scored, key=lambda x: x[1], reverse=True)


@dataclass
class MultiSpecializationScheduler:
    students_group: 'StudentsGroup'
    subject_group: 'SubjectGroup'
    rooms: List['Room']
    schedules: Dict[str, Dict[str, List['SubjectSession' | str]]] = field(default_factory=dict)
    used_slots: Set[Tuple[int, str, int]] = field(default_factory=set)

    def generate_all(self):
        grouped_sessions: Dict[str, List[SubjectSession]] = {}
        shared_course_schedules: Dict[str, Dict[str, List[SubjectSession | str]]] = {}

        # Step 1: Allocate course sessions only once per specialization-year
        for student in self.students_group.students:
            profile_name = f"{student.nume_specializare} {student.an_studiu}"
            subjects = self.subject_group.get_for_students(profile_name)
            grouped_sessions[profile_name] = []

            for subject in subjects:
                if subject.ore_curs:
                    grouped_sessions[profile_name] += [
                        SubjectSession(
                            name=subject.nume_materie,
                            type="curs",
                            how_many=student.nr_studenti
                        ) for _ in range(subject.ore_curs // 2)
                    ]

            # Allocate these course sessions once
            allocator = RoomAllocation(self.rooms, self.used_slots)
            shared_schedule = allocator.allocate(grouped_sessions[profile_name])
            shared_course_schedules[profile_name] = shared_schedule

        # Step 2: Allocate seminars/labs individually per semigroup
        for student in self.students_group.students:
            profile_name = f"{student.nume_specializare} {student.an_studiu}"
            subjects = self.subject_group.get_for_students(profile_name)

            for group in range(student.nr_grupe):
                for suffix in ['a', 'b']:
                    label = f"{profile_name}_grupa{group + 1}{suffix}"
                    sessions = []

                    for subject in subjects:
                        size = student.nr_studenti // student.nr_semigrupe
                        sessions += [
                            SubjectSession(
                                name=subject.nume_materie,
                                type=subject.tip_ora,
                                how_many=size,
                                sgr=label.split('_')[-1]
                            ) for _ in range(subject.ore_practice // 2)
                        ]

                    allocator = RoomAllocation(self.rooms, self.used_slots)
                    schedule = allocator.allocate(sessions)

                    # Inject the shared course sessions for this semigroup
                    for day in schedule:
                        for i in range(6):
                            shared_cell = shared_course_schedules[profile_name][day][i]
                            if isinstance(shared_cell, SubjectSession):
                                if not schedule[day][i]:
                                    schedule[day][i] = shared_cell
                                else:
                                    # Append without duplication
                                    if isinstance(schedule[day][i], SubjectSession):
                                        if schedule[day][i].name != shared_cell.name:
                                            schedule[day][i] = f"{schedule[day][i].render()}\n---\n{shared_cell.render()}"
                                    else:
                                        schedule[day][i] += f"\n---\n{shared_cell.render()}"

                    self.schedules[label] = schedule


    def get_schedule(self, profile_name: str) -> Dict[str, List['SubjectSession' | str]]:
        return self.schedules.get(profile_name, {})

    def list_profiles(self) -> List[str]:
        return list(self.schedules.keys())

    def get_combined_schedule(self, specialization_year: str) -> Dict[str, List['SubjectSession' | str]]:
        from collections import defaultdict

        combined_schedule = defaultdict(lambda: [""] * 6)

        for key, schedule in self.schedules.items():
            if key.startswith(specialization_year):
                for day, sessions in schedule.items():
                    for i, session in enumerate(sessions):
                        if session:
                            rendered = session if isinstance(session, str) else session.render()
                            if combined_schedule[day][i]:
                                combined_schedule[day][i] += f"\n---\n{rendered}"
                            else:
                                combined_schedule[day][i] = rendered

        return combined_schedule
