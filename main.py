from pprint import pprint
import matplotlib.pyplot as plt
import pandas as pd

from entity import StudentsGroup, SubjectGroup, RoomGroups


def allocate(students_group: StudentsGroup, subject_group: SubjectGroup, rooms_group: RoomGroups):
    af1_students = students_group.get_for_year_name("AF", 1)
    af1_subjects = subject_group.get_for_students("AF 1")
    af1_subject_sessions = [session for subject in af1_subjects for session in subject.get_sessions(af1_students)]
    for session in af1_subject_sessions:
        for room_type in ('curs', 'seminar', 'laborator'):
            for room in rooms_group.get_rooms_for_type(room_type):
                if session.type == room_type:
                    successful = room.allocate(session)
                    if successful:
                        break
    af1_subjects_names = [session.render() for session in af1_subject_sessions]
    pprint(af1_subjects)
    return {"Monday": af1_subjects_names[:6]}
    

def main():
    students_group = StudentsGroup.load()
    subject_group = SubjectGroup.load()
    rooms_group = RoomGroups.load()
    allocations = allocate(students_group, subject_group, rooms_group)
    plotting(allocations)

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

    table.scale(1, 4)
    plt.title("Weekly Schedule Table", fontweight='bold')
    plt.tight_layout()
    plt.savefig("weekly_schedule.png", dpi=300, bbox_inches="tight")
    plt.show()



if __name__ == "__main__":
    main()
