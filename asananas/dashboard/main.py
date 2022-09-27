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
    layout="wide",
    initial_sidebar_state="expanded",
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

with st.expander("Asana Credentials", expanded=False):
    asana_workspace_name = _credentials_input(
        "Asana Workspace Name", "ASANA_WORKSPACE_NAME"
    )
    asana_project_name = _credentials_input("Asana Project Name", "ASANA_PROJECT_NAME")
    asana_access_token = _credentials_input(
        "Asana Access Token", "ASANA_ACCESS_TOKEN", password=True
    )

# Sidbar Logo
# ###########

st.sidebar.markdown(f"Asananas v{asananas.__version__}")
st.sidebar.markdown("---")

# Load Data
# #########
df_asana_tasks = _load_data(
    asana_workspace_name, asana_project_name, asana_access_token
)

st.sidebar.markdown(
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
)

if st.sidebar.button("Clear Cache"):
    _load_data.clear()
    st.experimental_rerun()


# Resource Allocation
# ###################

st.markdown("---")

st.subheader("⌛ Resource Allocation")

st.markdown(
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
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


# Linear Bridge
# #############
st.markdown("---")

st.subheader("🔄 Linear Bridge")

st.markdown(
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
)

with st.expander("Settings", expanded=False):
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
