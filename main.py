import matplotlib.pyplot as plt
import pandas as pd

from entity import StudentsGroup, SubjectGroup, RoomGroups, MultiSpecializationScheduler


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
    schedule = scheduler.get_schedule(target_spec)
    plotting(schedule)


def plotting(data: dict[str, list[str]]):
    week_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    time_slots = [f"{hour}:00 - {hour + 2}:00" for hour in range(8, 20, 2)]

    schedule_df = pd.DataFrame('', index=time_slots, columns=week_days)

    for day, schedule in data.items():
        for index, subject in enumerate(schedule):
            if isinstance(subject, str):
                schedule_df.iloc[index, schedule_df.columns.get_loc(day)] = subject
            else:
                schedule_df.iloc[index, schedule_df.columns.get_loc(day)] = subject.render()

    fig, ax = plt.subplots(figsize=(12, 9))
    ax.axis('off')
    table = ax.table(cellText=schedule_df.values,
                     rowLabels=schedule_df.index,
                     colLabels=schedule_df.columns,
                     cellLoc='center',
                     loc='center')

    table.auto_set_font_size(False)
    table.set_fontsize(10)

    table.scale(1, 5)
    plt.title("Weekly Schedule Table", fontweight='bold')
    plt.tight_layout()
    plt.savefig("weekly_schedule.png", dpi=600, bbox_inches="tight")
    plt.show()


if __name__ == "__main__":
    main()
