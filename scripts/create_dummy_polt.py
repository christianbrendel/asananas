import pandas as pd
from asananas.allocation_management import (
    visualize_allocation_by_week,
    extract_allocation_data,
)

df_asana_tasks = pd.read_pickle("dummy_data.pkl")
(
    df_allocation_data,
    projects_with_no_allocation,
    projects_with_broken_allocation,
) = extract_allocation_data(df_asana_tasks, n_workdays_per_week=5)
v = [
    "Goofy",
    "DonaldDuck",
    "MickeyMouse",
    "Pluto",
    "MortimerMouse",
]

df_allocation_data = df_allocation_data[df_allocation_data.name.isin(v)]
fig = visualize_allocation_by_week(df_allocation_data, current_date="2022-09-30")

# save plotly figure as html
fig.write_html("../asananas/assets/demo_fig.html")
