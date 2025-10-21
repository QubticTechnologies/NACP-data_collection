#dashboards.py
import streamlit as st

def holder_dashboard():
    st.subheader("Holder Dashboard")
    st.info("This is where holders can view their data and reports.")

def agent_dashboard():
    st.subheader("Agent Dashboard")
    st.info("This is where agents review pending holders.")

def admin_dashboard():
    st.subheader("Admin Dashboard")
    st.info("This is where admin approves users and views reports.")
