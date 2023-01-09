import os

import streamlit as st

try:
    import pandas as pd

    from asananas import __version__ as VERSION
    from asananas.allocation_management import (
        extract_allocation_data,
        visualize_allocation_by_week,
    )
    from asananas.asana_connector import AsanaConnector
    from asananas.asana_linear_bridge import sync_asana_linear

    ASANANAS_DEMO_MODE = False
    LAYOUT = "centered"

except ImportError:

    import streamlit.components.v1 as components

    p = os.path.join(os.path.dirname(__file__), "..", "assets", "demo_fig.html")
    PLOTLY_DEMO_GRAPH = open(p, "r", encoding="utf-8").read()

    VERSION = "DEMO"
    ASANANAS_DEMO_MODE = True
    LAYOUT = "wide"


# Page Config
# ###########

st.set_page_config(
    page_title="Asananas Dashboard",
    page_icon="🍍",
    layout=LAYOUT,
    initial_sidebar_state="expanded",
)


# Image Paths
# ##########

fp = os.path.dirname(__file__)
FILE_PATH_LOGO = os.path.join(fp, "..", "assets", "logo3.png")
FILE_PATH_ASANA_EXAMPLE_TASK = os.path.join(
    fp, "..", "assets", "asana_example_task.png"
)
FILE_PATH_ASANA_LINEAR_MAPPING = os.path.join(
    fp, "..", "assets", "asana_linear_mapping.png"
)
FILE_PATH_DUMMY_DATA = os.path.join(fp, "..", "assets", "dummy_data.pkl")

# Helper Functions
# ################


def _credentials_text_input(variable_name, variable_env_name, password=False):
    variable_value = os.getenv(variable_env_name)

    if variable_value is None:
        variable_value = st.text_input(
            variable_name, type="password" if password else "default"
        )
        if variable_value == "":
            variable_value = None
    else:
        v = "*******" if password else variable_value
        st.success(
            f"{variable_name} found in environment variable {variable_env_name} = {v}"
        )

    return variable_value


def _credentials_select_input(variable_name, variable_env_name, options):

    variable_value = os.getenv(variable_env_name)

    if variable_value is None:
        variable_value = st.selectbox(f"Select {variable_name}", options)
    else:
        st.success(
            f"{variable_name} found in environment variable {variable_env_name} = {variable_value}"
        )

    return variable_value


@st.experimental_memo(ttl=3600)
def _get_workspaces(asana_access_token):
    asana_connector = AsanaConnector(access_token=asana_access_token)
    workspaces = asana_connector.get_workspaces()
    return {w["name"]: w["gid"] for w in workspaces}


@st.experimental_memo(ttl=3600)
def _get_projects(asana_access_token, workspace_id):
    asana_connector = AsanaConnector(access_token=asana_access_token)
    projects = asana_connector.get_projects_for_workspace(workspace_id)
    return {p["name"]: p["gid"] for p in projects}


@st.experimental_memo(ttl=3600)
def _load_data(asana_access_token, asana_project_id):
    return AsanaConnector(access_token=asana_access_token).get_all_tasks_for_project(
        asana_project_id
    )


# Header and Credentials
# ######################

st.header("Asananas Dashboard")

st.markdown(
    """
    Asananas helps you with your project management in [Asana](http://asana.com/). It assumes that a single Asana project, e.g. called "Company Workstreams", is used for high-level project planning of your company or your team. Different projects/workstreams are reflected in Asana as tasks in the dedicated Asana project. These Asana tasks can be assigned to different people and have a start and a due date.

    Asananas helps you to visualize the allocation of your team members over time. Additionally, it helps you to sync your Asana tasks with [Linear](http://linear.app/), a project management tool for software development teams. This is particularity useful for projects that are more technical in nature.
    """
)

with st.expander("Settings", expanded=False):

    st.markdown(
        "**ASANA**: To connect this dashboard to your Asana workspace, you need to provide your Asana access token and select a workspace and project. You can get your token [here](https://app.asana.com/0/my-apps)."
    )

    if ASANANAS_DEMO_MODE:
        st.success(
            "Asana Access Token found in environment variable ASANA_ACCESS_TOKEN = *******"
        )
        asana_workspace_name = st.selectbox(
            "Select Asana Workspace Name", ["My dummy company"]
        )
        asana_project_name = st.selectbox(
            "Select Asana Project Name", ["My dummy project"]
        )
        asana_access_token = "demo_token"
        asana_project_id = "dummy_project_id"

    else:

        asana_access_token = _credentials_text_input(
            "Asana Access Token", "ASANA_ACCESS_TOKEN", password=True
        )

        if asana_access_token is not None:

            workspaces = _get_workspaces(asana_access_token)
            asana_workspace_name = _credentials_select_input(
                "Asana Workspace Name", "ASANA_WORKSPACE_NAME", list(workspaces.keys())
            )
            asana_workspace_id = workspaces[asana_workspace_name]

            if asana_workspace_id is not None:
                projects = _get_projects(asana_access_token, asana_workspace_id)
                asana_project_name = _credentials_select_input(
                    "Asana Project Name", "ASANA_PROJECT_NAME", list(projects.keys())
                )
                asana_project_id = projects[asana_project_name]

        else:
            st.error("Provide a valid asana access token to continue.")
            asana_project_id = None

        st.markdown("---")

        st.markdown(
            "**LINEAR**: If you additionally want to use the Linear bridge you need to provide a Linear Access token as well as a team name."
        )

        linear_access_token = _credentials_text_input(
            "Linear Access Token", "LINEAR_ACCESS_TOKEN", password=True
        )
        linear_team_name = _credentials_text_input(
            "Liner Team Name", "LINEAR_TEAM_NAME"
        )

        st.markdown("---")

        st.markdown(
            "For convenience, you can provide all this information also via environment variables called `ASANA_ACCESS_TOKEN`, `ASANA_WORKSPACE_NAME`, `ASANA_PROJECT_NAME`, `LINEAR_ACCESS_TOKEN`, `LINEAR_TEAM_NAME`. This is useful in case this dashboard should be deployed for one specific team."
        )


with st.expander("Setup", expanded=False):
    st.markdown(
        """
    **Resource Allocation Management**: With a growing number of tasks the  resource allocation becomes harder and harder to oversee and it gets even more complicated when multiple people work on a single task. To avoid this problem, Asananas provides a simple way to visualize the resource allocation of your Asana project.
    To do so, you need to specify the required resources for each task in the task description by adding a custom field called  'Allocation'. The required resources are specified in the following format:
    - `Name1: 2d`: You can either specify the required resources in days. In this example, the task requires 2 days of Name1's time.
    - `Name1: 30%`: You can also specify the required resources in percent. In this example, the task requires 30% of the Name1's work time.
    - `Name1: 3d, Name2: 70%`: If you want to specify multiple resources, you can separate them by a comma.
    The image below shows an example task with the required resources specified in the Allocation field.
    """
    )
    _, c, _ = st.columns([1, 2, 1])
    with c:
        st.image(FILE_PATH_ASANA_EXAMPLE_TASK, caption="Asana Example Task")
    st.markdown(
        """
    ---

    **Linear Bridge**: From some tasks in your Asana project it might be useful to track the progress in Linear. Here we map a project in Asana to a team in Linear and a task in Asana to projects in Linear. See the image below for an illustration. To sync the start and due dates of the Asana task with the Linear project, provide your Linear API key and the Linear team name in the settings above and press the button below. All Asana tasks with the tag `Linear Project` will be synced (see screenshot above).
    """
    )
    _, c, _ = st.columns([1, 4, 1])
    with c:
        st.image(FILE_PATH_ASANA_LINEAR_MAPPING, caption="Mapping from Asana to Linear")


# Sidebar Logo
# ###########r


st.sidebar.image(FILE_PATH_LOGO, use_column_width=True)
st.sidebar.markdown(
    f"<div style='text-align: center;'>v{VERSION}<br><a href='https://www.github.com/christianbrendel/asananas'>GitHub</a> <a href='https://pypi.org/project/asananas'>PyPI</a> </div>",
    unsafe_allow_html=True,
)
st.sidebar.markdown("---")


# Load Data
# #########
if ASANANAS_DEMO_MODE:
    df_allocation_data = ["dummy"]
    projects_with_no_allocation = ["Dummy Project 123"]
    projects_with_broken_allocation = []

else:
    df_asana_tasks = _load_data(asana_access_token, asana_project_id)

    st.sidebar.markdown(
        "To speed up the dashboard, the data is cached for one hour. If you updated your Asana tasks press the button below to reload the data."
    )

    if st.sidebar.button("Clear Cache & Rerun"):
        _get_workspaces.clear()
        _get_projects.clear()
        _load_data.clear()
        st.experimental_rerun()

    (
        df_allocation_data,
        projects_with_no_allocation,
        projects_with_broken_allocation,
    ) = extract_allocation_data(df_asana_tasks, n_workdays_per_week=5)


# Resource Allocation
# ###################

st.markdown("---")

st.subheader("⌛ Resource Allocation")

if len(df_allocation_data) == 0:
    st.warning(
        f"Could not find any resource allocation data for the Asana project {asana_project_name}."
    )
else:
    st.markdown(
        "Individual tasks specified in your Asana project require different human resources. By specifying the required resources in the Asana task, you can visualize the resource allocation of your team. The following image shows the resource allocation by week:"
    )
    if ASANANAS_DEMO_MODE:
        components.html(PLOTLY_DEMO_GRAPH, height=1000, width=1000)

    else:
        # filter by name
        names = list(df_allocation_data.name.unique())
        selected_names = st.multiselect("Filter by names", names, default=names)
        df_allocation_data_plot = df_allocation_data[
            df_allocation_data["name"].isin(selected_names)
        ]

        # visualize
        fig = visualize_allocation_by_week(df_allocation_data_plot)
        st.plotly_chart(fig, theme=None)

    # warnings and errors
    if len(projects_with_no_allocation) > 0:
        st.warning(
            f"The following {len(projects_with_no_allocation)} projects have no resource allocated: {', '.join(projects_with_no_allocation)}"
        )
    if len(projects_with_broken_allocation) > 0:
        st.error(
            f"The following {len(projects_with_broken_allocation)} projects have an allocation that could not be decoded: {', '.join(projects_with_broken_allocation)}"
        )


# Linear Bridge
# #############

st.markdown("---")

st.subheader("🔄 Linear Bridge")

c1, c2, c3 = st.columns(3)
with c1:
    auto_create_linear_projects = st.checkbox("Auto create Linear projects", value=True)
with c2:
    sync_projects = st.checkbox("Sync project timelines", value=True)
with c3:
    cancel_linear_projects = st.checkbox("Auto cancel Linear projects", value=True)

if ASANANAS_DEMO_MODE:
    st.warning("Linear Bridge is disabled in demo mode.")

else:
    if (
        asana_project_id is not None
        and linear_access_token is not None
        and linear_team_name is not None
    ):
        if st.button("Run Asana-Linear Bridge"):
            with st.spinner("Sync in progress..."):

                sync_asana_linear(
                    asana_project_id,
                    asana_access_token,
                    linear_team_name,
                    linear_access_token,
                    auto_create_linear_projects,
                    sync_projects,
                    cancel_linear_projects,
                )
    else:
        st.warning(
            "Make sure you provided the linear access token, linear team name and linear access token in the settings above."
        )
