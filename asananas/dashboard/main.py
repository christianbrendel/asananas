import os

import streamlit as st

import asananas
from asananas.allocation_management import (
    extract_allocation_data,
    visualize_allocation_by_week,
)
from asananas.asana_connector import AsanaConnector
from asananas.asana_linear_bridge import sync_asana_linear

st.set_page_config(
    page_title="Asananas Dashboard",
    page_icon="🍍",
    layout="centered",
    initial_sidebar_state="expanded",
)

fp = os.path.dirname(__file__)
FILE_PATH_LOGO = os.path.join(fp, "..", "assets", "logo.jpg")
FILE_PATH_ASANA_EXAMPLE_TASK = os.path.join(
    fp, "..", "assets", "asana_example_task.png"
)
FILE_PATH_ASANA_LINEAR_MAPPING = os.path.join(
    fp, "..", "assets", "asana_linear_mapping.png"
)


# Helper Functions
# ################


def _credentials_input(variable_name, variable_env_name, password=False):
    variable_value = os.getenv(variable_env_name)
    if variable_value is None:
        variable_value = st.text_input(
            variable_name, type="password" if password else "default"
        )
    else:
        v = "*******" if password else variable_value
        st.success(
            f"{variable_name} found in environment variable {variable_env_name} = {v}"
        )
    return variable_value


@st.experimental_memo(ttl=3600)
def _load_data(asana_workspace_name, asana_project_name, asana_access_token):
    connector = AsanaConnector(
        asana_workspace_name, asana_project_name, asana_access_token
    )
    return connector.get_all_tasks()


# Header and Credentials
# ######################

st.header("Asananas Dashboard")

st.markdown(
    """
    Asananas helps you with your project management in [Asana](http://asana.com/). It assumes that a single Asana project, e.g. called "Company Workstreams", is used for high-level project planning of your company or your team. Different projects/workstreams are reflected in Asana as tasks in the dedicated Asana project. These Asana tasks can be assigned to different people and have a start and a due date.

    Asananas helps you to visualize the allocation of your team members over time. Additionally, it helps you to sync your Asana tasks with [Linear](http://linear.app/), a project management tool for software development teams. This is particularity useful for projects that are more technical in nature.
    """
)

with st.expander("Asana Credentials", expanded=False):

    st.markdown(
        """
        To connect this dashboard to your Asana workspace, you need to provide the following credentials:
        - `asana_workspace_name`: The name of your Asana workspace
        - `asana_project_name`: The name of the Asana project you want to visualize
        - `asana_access_token`: The access token of your Asana account. You can get your token [here](https://app.asana.com/0/my-apps).
        For convenience, you can also provide these credentials as environment variables.
        """
    )

    asana_workspace_name = _credentials_input(
        "Asana Workspace Name", "ASANA_WORKSPACE_NAME"
    )
    asana_project_name = _credentials_input("Asana Project Name", "ASANA_PROJECT_NAME")
    asana_access_token = _credentials_input(
        "Asana Access Token", "ASANA_ACCESS_TOKEN", password=True
    )

# Sidbar Logo
# ###########

st.sidebar.image(FILE_PATH_LOGO, use_column_width=True)
st.sidebar.markdown(f"Asananas v{asananas.__version__}")
st.sidebar.markdown("---")

# Load Data
# #########
df_asana_tasks = _load_data(
    asana_workspace_name, asana_project_name, asana_access_token
)

st.sidebar.markdown(
    "To speed up the dashboard, the data is cached for 1 hour. If you updated your Asana task press the button below to reload the data."
)

if st.sidebar.button("Clear Cache & Rerun"):
    _load_data.clear()
    st.experimental_rerun()


# Resource Allocation
# ###################

st.markdown("---")

st.subheader("⌛ Resource Allocation")


st.markdown(
    "Individual tasks specified in your Asana project require different human resources. By specifying the required resources in the Asana task, you can visualize the resource allocation of your team. The following image shows the resource allocation by week:"
)

(
    df_allocation_data,
    projects_with_no_allocation,
    projects_with_broken_allocation,
) = extract_allocation_data(df_asana_tasks, n_workdays_per_week=5)

# filter by name
names = list(df_allocation_data.name.unique())
selected_names = st.multiselect("Filter by names", names, default=names)
df_allocation_data_plot = df_allocation_data[
    df_allocation_data["name"].isin(selected_names)
]

# visualize
fig = visualize_allocation_by_week(df_allocation_data_plot)
st.plotly_chart(fig)

# warnings and errors
if len(projects_with_no_allocation) > 0:
    st.warning(
        f"The following {len(projects_with_no_allocation)} projects have no resource allocated: {', '.join(projects_with_no_allocation)}"
    )
if len(projects_with_broken_allocation) > 0:
    st.error(
        f"The follwing {len(projects_with_broken_allocation)} projects have an allocation that could not be decoded: {', '.join(projects_with_broken_allocation)}"
    )

# explanation
with st.expander("How to specify resources of a task in Asana", expanded=False):
    st.markdown(
        """
    With a growing number of tasks the  resource allocation becomes harder and harder to oversee and it gets even more complicated when multiple people work on a single task. To avoid this problem, Asananas provides a simple way to visualize the resource allocation of your Asana project.
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


# Linear Bridge
# #############

st.markdown("---")

st.subheader("🔄 Linear Bridge")

st.markdown(
    "From some tasks in your Asana project it might be useful to track the progress in Linear. Here we map a project in Asana to a team in Linear and a task in Asana to projects in Linear. See the image below for an illustration."
)
_, c, _ = st.columns([1, 4, 1])
with c:
    st.image(FILE_PATH_ASANA_LINEAR_MAPPING, caption="Mapping from Asana to Linear")
st.markdown(
    "To sync the start and due dates of the Asana task with the Linear project, provide your Linear API key and the Linear team name in the following field and press the button below. All Asana tasks with the tag `Linear Project` will be synced."
)

with st.expander("Settings", expanded=False):
    st.markdown(
        "To connect this dashboard to your Linear account, you need to provide the linear team name and the access token. For convenience, you can also provide these credentials as environment variables."
    )

    linear_team_name = _credentials_input("Liner Team Name", "LINEAR_TEAM_NAME")
    linear_access_token = _credentials_input(
        "Linear Access Token", "LINEAR_ACCESS_TOKEN", password=True
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        auto_create_linear_projects = st.checkbox(
            "Auto create Linear projects", value=True
        )
    with c2:
        sync_projects = st.checkbox("Sync project timelines", value=True)
    with c3:
        cancel_linear_projects = st.checkbox("Auto cancel Linear projects", value=True)

if st.button("Run Asana-Linear Bridge"):
    with st.spinner("Sync in progress..."):
        sync_asana_linear(
            asana_workspace_name,
            asana_project_name,
            asana_access_token,
            linear_team_name,
            linear_access_token,
            auto_create_linear_projects,
            sync_projects,
            cancel_linear_projects,
        )
