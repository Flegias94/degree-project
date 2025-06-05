from entity import StudentsGroup, SubjectGroup, RoomGroups, MultiSpecializationScheduler
from plot_schedule import plot_schedule


def main():
    students_group = StudentsGroup.load()
    subject_group = SubjectGroup.load()
    rooms_group = RoomGroups.load()

    scheduler = MultiSpecializationScheduler(
        students_group=students_group,
        subject_group=subject_group,
        rooms=rooms_group.rooms
    )

    scheduler.generate_all()

    target_spec = "IE 2"
    schedules = {k: scheduler.get_schedule(k) for k in scheduler.list_profiles() if k.startswith(target_spec)}
    plot_schedule(schedules, open_file=True)


if __name__ == "__main__":
    main()
