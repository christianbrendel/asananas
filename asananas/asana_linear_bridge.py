import typing as t
from datetime import datetime

import pandas as pd
from loguru import logger

from asananas.asana_connector import AsanaConnector
from asananas.linear_connector import LinearConnector

COLORS = [
    "#1F77B4",
    "#FF7F0E",
    "#2CA02C",
    "#D62728",
    "#9467BD",
    "#8C564B",
    "#CFECF9",
    "#7F7F7F",
    "#BCBD22",
    "#17BECF",
]


def sync_asana_linear(
    asana_project_id,
    asana_access_token,
    linear_team_name,
    linear_access_token,
    auto_create_linear_projects,
    sync_projects,
    cancel_linear_projects,
):

    logger.info("Fetching data from Asana")
    df_asana_tasks = AsanaConnector(
        access_token=asana_access_token
    ).get_all_tasks_for_project(asana_project_id)
    df_asana_tasks = df_asana_tasks[df_asana_tasks.asana_linear_project]

    logger.info("Fetching data from Linear")
    linear_connector = LinearConnector(access_token=linear_access_token)
    team_id, _, df_linear_projects = linear_connector.get_team_and_projects(
        linear_team_name
    )

    logger.info("Merging data")
    df = df_asana_tasks.merge(
        df_linear_projects,
        left_on="asana_task_name",
        right_on="linear_project_name",
        how="outer",
    )
    df["exists_on_asana"] = ~pd.isna(df.asana_task_id)
    df["exists_on_linear"] = ~pd.isna(df.linear_project_id)
    df["ongoing"] = pd.to_datetime(df.asana_start_on) < datetime.now()

    df_color_mapping = pd.DataFrame(
        [
            {"asana_section": s, "linear_color": COLORS[i % len(COLORS)]}
            for i, s in enumerate(df.asana_section.unique())
        ]
    )
    df = df.merge(df_color_mapping, on="asana_section", how="left")

    df = df.sort_values(by=["asana_section", "asana_start_on"]).reset_index(drop=True)

    for index, row in df.iterrows():

        if not row.asana_linear_project:
            continue

        # create linear project
        if (
            auto_create_linear_projects
            and row.exists_on_asana
            and not row.exists_on_linear
        ):

            row.linear_project_id = linear_connector.create_project(
                name=row["asana_task_name"],
                team_id=team_id,
            )

            row.exists_on_linear = True
            logger.info(
                f"Created Linear project {row.linear_project_id} for Asana task {row['asana_task_name']}"
            )

        # sync linear project
        if sync_projects & row.exists_on_asana & row.exists_on_linear:

            state = "planned"

            if row.ongoing:
                state = "started"

            if row.asana_completed:
                state = "completed"

            linear_connector.update_project(
                project_id=row.linear_project_id,
                start_date=row.asana_start_on,
                target_date=row.asana_due_on,
                state=state,
                description=f"Asana section: {row.asana_section}/nAsana URL: {row.asana_url}",
                color=row.linear_color,
                sort_order=index,
            )

            logger.info(
                f"Updated Linear project {row.linear_project_id} according to Asana task {row['asana_task_name']}"
            )

        # cancel linear project
        if cancel_linear_projects and not row.exists_on_asana and row.exists_on_linear:
            if row.linear_state != "cancelled":
                linear_connector.update_project(
                    project_id=row.linear_project_id, state="canceled"
                )
                logger.info(
                    f"Cancelled Linear project '{row.linear_project_name}' because no asana task exists."
                )
