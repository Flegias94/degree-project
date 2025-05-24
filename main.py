import json
from pprint import pprint
import matplotlib.pyplot as plt
import pandas as pd


def main():
    with open("subjects.json", "r") as f:
        subjects = json.load(f)
    with open("rooms.json", "r") as f:
        rooms = json.load(f)
    with open("students.json", "r") as f:
        students = json.load(f)
    # print(subjects)
    af1_subjects = []
    for subject in subjects:
        if subject["nume_specializare_mat"] == "AF 1":
            af1_subjects.append(subject)
    pprint(af1_subjects)
        
    # plotting({})

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
