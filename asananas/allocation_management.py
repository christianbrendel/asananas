import re
from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px


def _get_all_work_days(t1, t2, n_workdays_per_week):
    dates = []
    for i in range((t2 - t1).days + 1):
        date = t1 + timedelta(days=i)
        if date.isoweekday() <= n_workdays_per_week:
            dates.append(date)
    return dates


def extract_allocation_data(df_asana_tasks, n_workdays_per_week=5):

    projects_with_no_allocation = []
    projects_with_broken_allocation = []

    data = []

    for _, row in df_asana_tasks.iterrows():

        # skip tasks with no allocation
        if row.asana_allocation is None:
            projects_with_no_allocation.append(row.asana_task_name)
            continue

        # decode allocation
        pattern = r"([A-Za-z]+): ([0-9]+)(%|d)"
        allocations = re.findall(pattern, row.asana_allocation)
        if len(allocations) == 0:
            projects_with_broken_allocation.append(row.asana_task_name)
            continue

        # convert dates
        t1 = datetime.strptime(row.asana_start_on, "%Y-%m-%d")
        t2 = datetime.strptime(row.asana_due_on, "%Y-%m-%d")
        dates = _get_all_work_days(t1, t2, n_workdays_per_week=n_workdays_per_week)

        # build up data
        for date in dates:

            for allocation_info in allocations:

                allocation_value = float(allocation_info[1])
                allocation_unit = allocation_info[2]

                if allocation_unit == "%":
                    allocation = allocation_value / 100
                elif allocation_unit == "d":
                    allocation = allocation_value / len(dates)

                data.append(
                    {
                        "date": date,
                        "name": allocation_info[0],
                        "allocation": allocation,
                        "project": row.asana_task_name,
                    }
                )

    return (
        pd.DataFrame(data),
        projects_with_no_allocation,
        projects_with_broken_allocation,
    )


def visualize_allocation_by_week(
    df_allocation_data, n_workdays_per_week=5, current_date=None
):

    if current_date is None:
        t = datetime.now()
    else:
        t = datetime.strptime(current_date, "%Y-%m-%d")

    n_weeks_into_past = 4
    n_weeks_into_future = 12

    t0 = t - timedelta(days=7 * n_weeks_into_past)
    x0 = f"{t0.year}-CW{t0.isocalendar().week:02d}"

    t1 = t + timedelta(days=7 * n_weeks_into_future)
    x1 = f"{t1.year}-CW{t1.isocalendar().week:02d}"

    # create the week field
    df_allocation_data["week"] = df_allocation_data["date"].apply(
        lambda x: f"{x.isocalendar().year}-CW{x.isocalendar().week:02d}"
    )

    # group by name, project and week
    df_tmp = (
        df_allocation_data.groupby(["name", "project", "week"])
        .aggregate(
            allocation=("allocation", "first"),
            n_days_in_this_week=("date", "count"),
            week_of=("date", "min"),
        )
        .reset_index()
        .sort_values("week")
    )
    df_tmp["week_of"] = df_tmp.week_of.apply(lambda date: date.strftime("%Y-%m-%d"))
    df_tmp["allocation"] = (
        df_tmp.allocation * df_tmp.n_days_in_this_week / n_workdays_per_week
    )

    # time of interest only
    df_tmp = df_tmp[(df_tmp.week > x0) & (df_tmp.week <= x1)]

    # basic bar plot
    fig = px.bar(
        df_tmp,
        x="week",
        y="allocation",
        color="project",
        title="Resource Allocation by Week",
        facet_row="name",
        hover_data=["week_of"],
    )

    # sort x-axis alpabetically
    # fig.update_xaxes(categoryorder="array", categoryarray=df_tmp.week.unique())

    # maximum allocation marker
    fig.add_hline(y=1)

    # grey out the past
    fig.add_vrect(
        x0=-1, x1=n_weeks_into_past - 1, line_width=0, fillcolor="black", opacity=0.4
    )

    # update axis
    fig.update_xaxes(
        showline=True, linecolor="black", linewidth=2, mirror=True, tickangle=90
    )
    fig.update_yaxes(
        showline=True, linecolor="black", linewidth=2, mirror=True, range=[0, 1.5]
    )

    # update the size of the plot
    fig.update_layout(
        autosize=False,
        width=1000,
        height=df_tmp.name.nunique() * 200,
    )

    return fig
