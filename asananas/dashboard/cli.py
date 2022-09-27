import sys
from os import path as p

from streamlit.web import cli as stcli


def run():
    dashboard_file = p.join(p.abspath(p.dirname(__file__)), "main.py")
    sys.argv = ["streamlit", "run", dashboard_file]
    sys.exit(stcli.main())
