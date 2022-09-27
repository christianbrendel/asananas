import os
import typing as t
from datetime import datetime

import pandas as pd
import requests
from loguru import logger


class LinearConnector:

    url = "https://api.linear.app/graphql"

    def __init__(self, access_token: str = None) -> None:

        if access_token is None:
            access_token = os.getenv("LINEAR_ACCESS_TOKEN")

        if access_token is None:
            raise Exception("No Linear access token provided")

        self.access_token = access_token

        self._check_permissions()

    def _post_request(self, query, variables={}):
        r = requests.post(
            self.url,
            json={"query": query, "variables": variables},
            headers={"Authorization": self.access_token},
        )
        if r.status_code == 200:
            return r.status_code, r.json()
        else:
            raise Exception(
                f"LinearConnector initialization failed: {r.status_code} {r.text}"
            )

    def _check_permissions(self):
        query = """
            query Me {
                viewer {
                    id
                    name
                    email
                }
            }"""
        return self._post_request(query)

    def get_team_and_projects(self, team_name: str) -> t.Tuple[str, str, dict]:
        query = """
            query ProjectsByTeam($team_name: String){
                teams(filter: {name: {eq: $team_name}}) {
                    nodes {
                        id
                        name
                        projects{
                            nodes{
                                id
                                name
                                startDate
                                targetDate
                                state
                                url
                            }
                        }
                    }
                }
            }
            """
        variables = {"team_name": team_name}
        _, response = self._post_request(query, variables)
        response = response["data"]["teams"]["nodes"]
        assert len(response) == 1, f"We expect only one team with the name {team_name}"

        team_id = response[0]["id"]
        team_name = response[0]["name"]
        projects = response[0]["projects"]["nodes"]

        projects = [
            {
                "linear_project_id": p["id"],
                "linear_project_name": p["name"],
                "linear_start_date": p["startDate"],
                "linear_target_date": p["targetDate"],
                "linear_state": p["state"],
                "linear_url": p["url"],
            }
            for p in projects
        ]

        if len(projects) == 0:
            columns = [
                "linear_project_id",
                "linear_project_name",
                "linear_start_date",
                "linear_target_date",
                "linear_state",
                "linear_url",
            ]
            projects = pd.DataFrame(columns=columns)
        else:
            projects = pd.DataFrame(projects)

        return team_id, team_name, projects

    def create_project(self, name: str, team_id: str) -> str:
        query = """
            query ProjectsByName($project_name: String!) {
                projects(filter: {name: {eq: $project_name}}) {
                    nodes {
                        id
                        teams {
                            nodes {
                                name
                                id
                            }
                        }
                    }
                }
            }
        """
        variables = {"project_name": name}
        _, response = self._post_request(query, variables)
        project_ids = [
            tmp["id"]
            for tmp in response["data"]["projects"]["nodes"]
            if tmp["teams"]["nodes"][0]["id"] == team_id
        ]

        if len(project_ids) > 0:
            logger.warning(
                f"Project {name} already exists in team {team_id}. Skipping creation."
            )
            return project_ids[0]

        query = """
            mutation ProjectCreate($project_name: String!, $team_id: String!) {
                projectCreate(
                    input: {
                        name: $project_name,
                        teamIds: [$team_id]
                        state: "planned"
                    }
                ) {
                    success 
                    project {
                        id
                    }
                }
            }
            """
        variables = {"project_name": name, "team_id": team_id}
        _, response = self._post_request(query, variables)

        return response["data"]["projectCreate"]["project"]["id"]

    def update_project(
        self,
        project_id: str,
        start_date: str = None,
        target_date: str = None,
        state: str = None,
        description: str = None,
        color: str = None,
        sort_order: int = None,
    ) -> str:

        # input validation
        try:
            if start_date is not None:
                t1 = datetime.strptime(start_date, "%Y-%m-%d")
            if target_date is not None:
                t2 = datetime.strptime(target_date, "%Y-%m-%d")

        except ValueError:
            raise Exception("Incorrect date format, should be YYYY-MM-DD")

        if (start_date is not None) and (target_date is not None) and (t1 > t2):
            raise Exception("Start date should be before target date")

        if state not in [
            "backlog",
            "planned",
            "started",
            "paused",
            "completed",
            "canceled",
            None,
        ]:
            raise Exception(
                "State should be one of: backlog, planned, in_progress, paused, completed, canceled"
            )

        # query
        query = """
            mutation UpdateProject($project_id: String!, $startDate: TimelessDate, $targetDate: TimelessDate, $description: String, $state: String = "planned", $color: String, $sortOrder: Float) {
                projectUpdate(
                    id: $project_id
                    input: {
                        startDate: $startDate
                        targetDate: $targetDate
                        description: $description
                        state: $state
                        color: $color
                        sortOrder: $sortOrder
                    }
                ){
                    success
                    project {
                        id
                    }
                }
            }
            """

        # variables
        variables = {"project_id": project_id}
        if start_date is not None:
            variables["startDate"] = start_date
        if target_date is not None:
            variables["targetDate"] = target_date
        if description is not None:
            variables["description"] = description
        if state is not None:
            variables["state"] = state
        if color is not None:
            variables["color"] = color
        if sort_order is not None:
            variables["sort_order"] = sort_order

        # execution
        _, response = self._post_request(query, variables)
        if "errors" in response:
            raise Exception(f"LinearConnector update failed: {response['errors']}")
        return response["data"]["projectUpdate"]["project"]["id"]
