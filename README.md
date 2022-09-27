<div align="center">
 
# Asananas
 
</div>
 
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
 
Asananas helps you with your project management in [Asana](http://asana.com/). It assumes that a single Asana project, e.g. called "Company Workstreams", is used for high-level project planning of your company or your team. Different projects/workstreams are reflected in Asana as tasks in the dedicated Asana project. These Asana tasks can be assigned to different people and have a start and a due date.
 Asananas helps you to visualize the allocation of your team members over time. Additionally, it helps you to sync your Asana tasks with [Linear](http://linear.app/), a project management tool for software development teams. This is particularly useful for projects that are more technical in nature.
 
## Disclaimer
 
This package is a PoC that has been developed within a few hours. Bit and pieces of the code are unclean and very hacky. For a more detailed list of the limitations see the section "Limitations & Improvements" below.
 
Additionally it is worth mentioning that about 75% of all the code (including the markdown text in the dashboard) has been suggested by [GitHub Copilot](https://github.com/features/copilot) and the logo has been created by the latest [stable-diffusion](https://replicate.com/blog/run-stable-diffusion-on-m1-mac) model using the prompt *"blabla"*.
 
## Quick start
To start quickly simply install the package via pip and launch the built-in dashboard. The dashboard explains how to set up the link with Asana and Linear.
 
```
pip install asananas
asananas-dashboard
```
 
Two use the two main features of Asananas you do not necessarily need the dashboard but you can simply use the following commands in the terminal
 
```
# get the allocation visualization
asananas-allocation -path "allocation.html" ...
 
# sync Linear with Asana
asananas-sync-linear -asana_workspace_name "your_asana_workspace" ...
```
 
To got even lower level you can also use the individual agents of the package, e.g.
 
```python
from asananas.asana_connector import AsanaConnector
from asananas.allocation_management import extract_allocation_data, visualize_allocation_by_week
  
asana_connector = AsanaConnector(workspace_name="foo", project_name="bar", access_token="my_secret")
df_asana_tasks = asana_connector.get_all_tasks()
df_allocation_data, _, _ = extract_allocation_data(df_asana_tasks, n_workdays_per_week=5)
fig = visualize_allocation_by_week(df_allocation_data)
fig.write_html("my_allocation_plot.html")
```
 
## Setup Dev Environment
 
To develop the Asananas package feel free to use the pre-defined conda environment. To set it up simply run the following two lines of code:
 
```
conda env create --file conda.yml
```
 
You also find a makefile that helps you to format your code, check the code coverage of the unit tests and check your docstring. Please always check your code before you push using the following commands:
 
```
make format-code
make check-docstrings
```
 
or simply use `make all`.
 
 
## Limitations & Improvements
 
- The package is not very well tested, in particular there is not a single unit test.
- The package does not contain proper error management, e.g. there are no checks whether the allocation field actually exists in the Asana tasks. In general, the dashboard is not prepared for wrong user interaction and does not really help solving the issue.
- The package assumes you know the name of your Asana Workspace or Project Name. Fetching this information and providing some nice GUI to select the desired e.g. project would be a nice feature.
- The code is hardly documented.

