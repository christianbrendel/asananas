import os
import typing as t

import asana
import pandas as pd


class AsanaConnector:
    def __init__(self, access_token: str = None):

        if access_token is None:
            access_token = os.getenv("ASANA_ACCESS_TOKEN")

        if access_token is None:
            raise Exception("No Asana access token provided")

        self.client = asana.Client.access_token(access_token)

    def get_workspaces(self):
        return list(self.client.workspaces.find_all())

    def get_projects_for_workspace(self, workspace_id):
        return list(self.client.projects.find_by_workspace(workspace_id))

    def _find_section_by_project_id(self, task_info, project_id):
        for membership in task_info["memberships"]:
            if membership["project"]["gid"] == project_id:
                if "section" in membership:
                    return membership["section"]["name"]
        return None

    def _find_allocation(self, task_info):
        for custom_field in task_info["custom_fields"]:
            if custom_field["name"] == "Allocation":
                return custom_field["text_value"]
        return None

    def get_all_tasks_for_project(self, project_id) -> t.List[t.Dict]:
        task_infos = []
        for task in self.client.tasks.find_by_project(project_id):
            task_info = self.client.tasks.get_task(task["gid"])

            if task_info["resource_subtype"] != "default_task":
                continue

            assignee = (
                None if task_info["assignee"] is None else task_info["assignee"]["name"]
            )
            tags = [t["name"] for t in task_info["tags"]]

            task_infos.append(
                {
                    "asana_task_id": task_info["gid"],
                    "asana_task_name": task_info["name"],
                    "asana_start_on": task_info["start_on"],
                    "asana_due_on": task_info["due_on"],
                    "asana_completed": task_info["completed"],
                    "asana_assignee": assignee,
                    "asana_url": task_info["permalink_url"],
                    "asana_linear_project": "Linear Project" in tags,
                    "asana_section": self._find_section_by_project_id(
                        task_info, project_id
                    ),
                    "asana_allocation": self._find_allocation(task_info),
                }
            )

        if len(task_infos) == 0:
            columns = [
                "asana_task_id",
                "asana_task_name",
                "asana_start_on",
                "asana_due_on",
                "asana_completed",
                "asana_assignee",
                "asana_url",
                "asana_linear_project",
                "asana_section",
                "asana_allocation",
            ]
            return pd.DataFrame(columns=columns)

        return pd.DataFrame(task_infos)
