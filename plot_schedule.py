import os
import textwrap

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ROW_HEIGHT = 2.0
FIGURE_WIDTH_PER_COL = 2.5

FONT_SIZE_TITLE = 16
FONT_SIZE_GROUP_HEADER = 14
FONT_SIZE_WEEKDAY = 18
FONT_SIZE_HOUR_LABEL = 13
FONT_SIZE_CELL_TEXT = 11
FONT_SIZE_CURS_CELL = 16

COLOR_CURS = "#666666"
COLOR_SEMINAR = "#7B3F3F"
COLOR_LAB = "#2E5A2E"
COLOR_OTHER = "#888888"
COLOR_DAY_BG = "#cccccc"


def draw_cell(ax, row, col, colspan, row_height, text, color, fontsize=FONT_SIZE_CELL_TEXT):
    y = row * row_height
    wrapped = "\n".join(textwrap.wrap(text, width=25))
    rect = Rectangle((col, y), colspan, row_height, facecolor=color, edgecolor='black')
    ax.add_patch(rect)
    ax.text(col + colspan / 2, y + row_height / 2, wrapped,
            ha='center', va='center', fontsize=fontsize, color='white')


def draw_group_headers(ax, semigroups, row_height, total_rows):
    for j, sg in enumerate(semigroups):
        y = total_rows * row_height + 1.5 * row_height
        ax.text(j + 0.5, y, sg, ha='center', va='center', fontsize=FONT_SIZE_GROUP_HEADER, fontweight='bold')


def draw_grid(ax, total_rows, row_height, n_cols, schedule_by_group, semigroups, time_labels, week_days):
    for i in range(total_rows + 1):
        y = i * row_height
        ax.axhline(y, color='black', linewidth=0.5)

    for j in range(n_cols + 1):
        skip = False
        for day in week_days:
            for t_idx, hour in enumerate(time_labels):
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

    bottom = total_rows * row_height + row_height
    top = total_rows * row_height + 2.0 * row_height
    for j in range(n_cols + 1):
        ax.plot([j, j], [bottom, top], color='black', linewidth=0.5)
    ax.plot([0, n_cols], [top, top], color='black', linewidth=0.5)


def draw_day_and_slots(ax, day, i, week_days, time_labels, schedule_by_group, semigroups, n_cols, total_rows,
                       rows_per_day, row_height, colors):
    base_row = total_rows - i * rows_per_day - 1
    is_last_day = (i == len(week_days) - 1)
    if not is_last_day or any(any(schedule_by_group.get(sg, {}).get(day, [])) for sg in semigroups):
        y_day = (base_row + 1) * row_height
        ax.add_patch(Rectangle((0, y_day), n_cols, row_height, facecolor=COLOR_DAY_BG, edgecolor='black'))
        ax.text(n_cols / 2, y_day + row_height / 2, day, ha='center', va='center', fontsize=FONT_SIZE_WEEKDAY,
                fontweight='bold')

    for t_idx, hour in enumerate(time_labels):
        row = base_row - t_idx
        y = row * row_height
        ax.text(-0.1, y + row_height / 2, hour, ha='right', va='center', fontsize=FONT_SIZE_HOUR_LABEL)

        text_map = {}
        for col, sg in enumerate(semigroups):
            session_list = schedule_by_group.get(sg, {}).get(day, [])
            session = session_list[t_idx] if t_idx < len(session_list) else ""
            if hasattr(session, "render"):
                session = session.render()
            if not session:
                continue
            text_map.setdefault(session, []).append(col)

        for text, cols in text_map.items():
            lower = text.lower()
            typ = "curs" if "curs" in lower else "lab" if "lab" in lower else "seminar" if "sem" in lower else "other"
            color = colors.get(typ, "#888888")
            start_col = min(cols)
            end_col = max(cols)
            colspan = end_col - start_col + 1 if typ == "curs" else 1

            if typ == "curs":
                draw_cell(ax, row, start_col, colspan, row_height, text, color, fontsize=FONT_SIZE_CURS_CELL)
            else:
                for col in cols:
                    draw_cell(ax, row, col, 1, row_height, text, color)

        for col in range(n_cols):
            if col not in [c for cols in text_map.values() for c in cols]:
                draw_cell(ax, row, col, 1, row_height, "", "white")


def plot_schedule(schedule_by_group: dict[str, dict[str, list[str]]], open_file=False,
                  save_path="schedule_plot.png"):
    semigroups = sorted(schedule_by_group.keys())
    week_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    time_labels = ["08:00", "10:00", "12:00", "14:00", "16:00", "18:00"]
    row_height = ROW_HEIGHT
    rows_per_day = 1 + len(time_labels)
    total_rows = rows_per_day * len(week_days) - 1
    n_cols = len(semigroups)

    fig_width = n_cols * FIGURE_WIDTH_PER_COL
    fig_height = total_rows * row_height
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    draw_grid(ax, total_rows, row_height, n_cols, schedule_by_group, semigroups, time_labels, week_days)
    draw_group_headers(ax, semigroups, row_height, total_rows)

    colors = {
        "curs": COLOR_CURS,
        "seminar": COLOR_SEMINAR,
        "lab": COLOR_LAB,
        "other": COLOR_OTHER,
    }

    for i, day in enumerate(week_days):
        draw_day_and_slots(ax, day, i, week_days, time_labels, schedule_by_group, semigroups, n_cols, total_rows,
                           rows_per_day, row_height, colors)

    ax.set_xlim(0, n_cols)
    ax.set_ylim(0, total_rows * row_height + 2 * row_height)
    ax.axis('off')
    ax.set_title("Schedule", fontsize=FONT_SIZE_TITLE, fontweight='bold')
    plt.tight_layout()
    plt.savefig(save_path, dpi=240, bbox_inches="tight")
    if open_file:
        os.startfile(save_path)
