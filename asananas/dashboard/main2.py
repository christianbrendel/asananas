import streamlit as st
import streamlit.components.v1 as components

st.header("test html import")
source_code = open("asananas/assets/demo_fig.html", "r", encoding="utf-8").read()
components.html(source_code, height=1800, width=1200)
