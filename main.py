from dataclasses import dataclass
import json
from pprint import pprint
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


def main():
    with open("subjects.json", "r") as f:
        raw_subjects = json.load(f)
    with open("rooms.json", "r") as f:
        rooms = json.load(f)
    with open("students.json", "r") as f:
        students = json.load(f)
    # print(subjects)
    subjects: list[Subject] = [Subject(**subject) for subject in raw_subjects]
    af1_subjects: list[Subject] = []
    for subject in subjects:
        if subject.nume_specializare_mat == "AF 1":
            af1_subjects.append(subject)
    pprint(af1_subjects)
    af1_subjects_names = [subject.nume_materie for subject in af1_subjects]
        
    plotting({"Monday": af1_subjects_names})

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
