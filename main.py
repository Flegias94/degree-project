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

    # Grid (horizontal lines)
    for i in range(total_rows + 1):
        y = i * row_height
        ax.axhline(y, color='black', linewidth=0.5)

    # Grid (vertical lines) – skip if line falls inside a merged 'curs' cell
    for j in range(n_cols + 1):
        skip = False
        for day in week_days:
            for t_idx, hour in enumerate(time_labels):
                # Collect all columns where this time slot is a 'curs'
                curs_cols = []
                for idx, sg in enumerate(semigroups):
                    session_list = schedule_by_group.get(sg, {}).get(day, [])
                    if t_idx < len(session_list):
                        session = session_list[t_idx]
                        if hasattr(session, "render"):
                            session = session.render()
                        if isinstance(session, str) and "curs" in session.lower():
                            curs_cols.append(idx)
                if len(curs_cols) > 1 and min(curs_cols) < j <= max(curs_cols):
                    skip = True
                    break
            if skip:
                break
        if not skip:
            ax.axvline(j, color='black', linewidth=0.5)

        # Extend vertical lines through the weekday + group header rows
        group_header_bottom = total_rows * row_height + row_height  # where "Monday" row starts
        group_header_top = total_rows * row_height + 2.0 * row_height  # top edge of group label row

        for j in range(n_cols + 1):
            ax.plot([j, j], [group_header_bottom, group_header_top], color='black', linewidth=0.5)

        # Draw top horizontal line above the group header row
        ax.plot([0, n_cols], [group_header_top, group_header_top], color='black', linewidth=0.5)

    # Header (shifted group names one row higher)
    for j, sg in enumerate(semigroups):
        group_y_center = total_rows * row_height + 1.5 * row_height
        ax.text(j + 0.5, group_y_center,
                sg, ha='center', va='center', fontsize=12, fontweight='bold')

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

            # Draw empty cells where nothing was placed
            for col in range(n_cols):
                if col not in [c for cols in text_map.values() for c in cols]:
                    draw_cell(ax, row, col, 1, row_height, "", "white")

    ax.set_xlim(0, n_cols)
    ax.set_ylim(0, total_rows * row_height + 2 * row_height)
    ax.axis('off')
    ax.set_title("Schedule", fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig("schedule_plot.png", dpi=240, bbox_inches="tight")


def draw_cell(ax, row, col, colspan, row_height, text, color, edgecolor='black', textcolor='white'):
    y = row * row_height
    wrapped = "\n".join(textwrap.wrap(text, width=25))
    rect = Rectangle((col, y), colspan, row_height,
                     facecolor=color, edgecolor=edgecolor)
    ax.add_patch(rect)
    if text.strip():
        ax.text(col + colspan / 2, y + row_height / 2, wrapped,
                ha='center', va='center', fontsize=9, color=textcolor)


if __name__ == "__main__":
    main()
