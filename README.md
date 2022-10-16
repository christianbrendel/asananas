<div align="center">
 
<p align="center">
  <img src="https://raw.githubusercontent.com/christianbrendel/asananas/main/asananas/assets/logo2.png" width=400px></img>
</p>

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://christianbrendel-asananas-asananasdashboardmain-0vvuq2.streamlitapp.com)

---

</div>
 
 
Asananas helps you with your project management in [Asana](http://asana.com/). It assumes that a single Asana project, e.g. called "Company Workstreams", is used for high-level project planning of your company or your team. Different projects/workstreams are reflected in Asana as tasks in the dedicated Asana project. These Asana tasks can be assigned to different people and have a start and a due date.
Asananas helps you to visualize the allocation of your team members over time. Additionally, it helps you to sync your Asana tasks with [Linear](http://linear.app/), a project management tool for software development teams. This is particularly useful for projects that are more technical in nature.

![Example Resource Allocation](https://github.com/christianbrendel/asananas/blob/main/asananas/assets/resource_allocation_example.png?raw=true)

## Disclaimer
 
This package is a PoC that has been developed within a few hours. Bit and pieces of the code are unclean and very hacky. For a more detailed list of the limitations see the section "Limitations & Improvements" below.
 
Additionally it is worth mentioning that about 75% of all the code (including the markdown text in the dashboard) has been suggested by [GitHub Copilot](https://github.com/features/copilot) and the logo has been created by the a [stable-diffusion](https://replicate.com/blog/run-stable-diffusion-on-m1-mac) model using the prompt *"A cartoon of a pineapple wearing sunglasses while flying through the sky"*. 🙂

## Quick Start
To start quickly simply install the package via pip and launch the built-in dashboard. The dashboard explains how to set up the link with Asana and Linear.
 
```
pip install asananas
asananas-dashboard
```
 
You can also use the low-level function of the package, e.g.
 
```python
from asananas.asana_connector import AsanaConnector
from asananas.allocation_management import extract_allocation_data, visualize_allocation_by_week
  
asana_connector = AsanaConnector(access_token="foo")

workspaces = asana_connector.get_workspaces()
workspace_id = workspaces[0]["gid"]

projects = asana_connector.get_projects_for_workspace(workspace_id)
project_id = projects[0]["gid"]

df_asana_tasks = asana_connector.get_all_tasks_for_project(project_id)

df_allocation_data, _, _ = extract_allocation_data(df_asana_tasks, n_workdays_per_week=5)
fig = visualize_allocation_by_week(df_allocation_data)
fig.write_html("my_allocation_plot.html")
```
  
## Limitations & Improvements
 
- The package is not very well tested, in particular there is not a single unit test.
- The package does not contain proper error management, e.g. there are no checks whether the allocation field actually exists in the Asana tasks. In general, the dashboard is not prepared for wrong user interaction and does not really help solving the issue.
- The code is hardly documented.

