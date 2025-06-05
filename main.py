import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Rectangle
import textwrap

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
    schedules = {k: scheduler.get_schedule(k) for k in scheduler.list_profiles() if k.startswith(target_spec)}
    plotting(schedules)



def plotting(schedule_by_group: dict[str, dict[str, list[str]]]):
    semigroups = sorted(schedule_by_group.keys())
    week_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    time_labels = ["08:00", "10:00", "12:00", "14:00", "16:00", "18:00"]

    row_height = 2.0  # just a bit taller
    rows_per_day = 1 + len(time_labels)
    total_rows = rows_per_day * len(week_days)
    n_cols = len(semigroups)

    fig_width = n_cols * 2.5
    fig_height = total_rows * row_height
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    # Grid
    for i in range(total_rows + 1):
        y = i * row_height
        ax.axhline(y, color='black', linewidth=0.5)
    for j in range(n_cols + 1):
        ax.axvline(j, color='black', linewidth=0.5)

    # Header
    for j, sg in enumerate(semigroups):
        ax.text(j + 0.5, total_rows * row_height + 0.3 * row_height,
                sg, ha='center', va='bottom', fontsize=10, fontweight='bold')

    # Colors
    colors = {
        "curs": "#666666",
        "seminar": "#7B3F3F",
        "lab": "#2E5A2E",
        "other": "#888888"
    }

    for i, day in enumerate(week_days):
        base_row = total_rows - i * rows_per_day - 1

        # Day title row
        y_day = (base_row + 1) * row_height
        ax.add_patch(Rectangle((0, y_day), n_cols, row_height,
                               facecolor="#cccccc", edgecolor='black'))
        ax.text(n_cols / 2, y_day + row_height / 2, day,
                ha='center', va='center', fontsize=11, fontweight='bold')

        # Time slots
        for t_idx, hour in enumerate(time_labels):
            row = base_row - t_idx
            y = row * row_height
            ax.text(-0.1, y + row_height / 2, hour, ha='right', va='center', fontsize=9)

            # Group content
            text_map = {}
            for col, sg in enumerate(semigroups):
                session_list = schedule_by_group.get(sg, {}).get(day, [])
                session = session_list[t_idx] if t_idx < len(session_list) else ""
                if hasattr(session, "render"):
                    session = session.render()
                if not session:
                    continue
                text_map.setdefault(session, []).append(col)

            # Draw sessions
            for text, cols in text_map.items():
                lower = text.lower()
                typ = "curs" if "curs" in lower else "lab" if "lab" in lower else "seminar" if "sem" in lower else "other"
                color = colors.get(typ, "#888888")
                start_col = min(cols)
                end_col = max(cols)
                colspan = end_col - start_col + 1 if typ == "curs" else 1

                if typ == "curs":
                    draw_cell(ax, row, start_col, colspan, row_height, text, color)
                else:
                    for col in cols:
                        draw_cell(ax, row, col, 1, row_height, text, color)

    ax.set_xlim(0, n_cols)
    ax.set_ylim(0, total_rows * row_height + 1.5 * row_height)
    ax.axis('off')
    ax.set_title("Schedule", fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.show()

def draw_cell(ax, row, col, colspan, row_height, text, color):
    y = row * row_height
    wrapped = "\n".join(textwrap.wrap(text, width=25))
    rect = Rectangle((col, y), colspan, row_height,
                     facecolor=color, edgecolor='black')
    ax.add_patch(rect)
    ax.text(col + colspan / 2, y + row_height / 2, wrapped,
            ha='center', va='center', fontsize=9, color='white')

if __name__ == "__main__":
    main()
