import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="CyberNova Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# SIMPLE USER AUTHENTICATION
# =========================================================

USERS = {
    "admin": {
        "password": "rory333",
        "role": "Admin"
    },
    "sales": {
        "password": "sales_nova",
        "role": "Sales & Marketing"
    }
}

# Session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "role" not in st.session_state:
    st.session_state.role = None

if "username" not in st.session_state:
    st.session_state.username = None


# =========================================================
# LOGIN FUNCTION
# =========================================================
def login():

    st.markdown(
        """
        <h1 style='text-align:center; color:#00BFFF;'>
        CyberNova Analytics Dashboard
        </h1>
        """,
        unsafe_allow_html=True
    )

    st.markdown("## Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if username in USERS and USERS[username]["password"] == password:

            st.session_state.logged_in = True
            st.session_state.role = USERS[username]["role"]
            st.session_state.username = username

            st.success("Login Successful")
            st.rerun()

        else:
            st.error("Invalid Username or Password")


# =========================================================
# LOGOUT FUNCTION
# =========================================================
def logout():

    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.username = None

    st.rerun()


# =========================================================
# LOGIN SCREEN
# =========================================================
if not st.session_state.logged_in:
    login()
    st.stop()

# =========================================================
# LOAD DATA
# =========================================================
@st.cache_data
def load_data():

    df = pd.read_csv("cybernova_dataset.csv")

    # Clean columns
    df.columns = df.columns.str.strip().str.lower()

    # Convert timestamp
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    return df


df = load_data()

# =========================================================
# SIDEBAR / NAVIGATION PANE
# =========================================================
st.sidebar.title("CyberNova Navigation")

st.sidebar.markdown("---")

# User Info
st.sidebar.success(f"Logged in as: {st.session_state.username}")
st.sidebar.info(f"Role: {st.session_state.role}")

st.sidebar.markdown("---")

# Dashboard Navigation
view = st.sidebar.radio(
    "Select Dashboard",
    [
        "Overview",
        "Sales",
        "Marketing",
        "Geographic"
    ]
)

st.sidebar.markdown("---")

# =========================================================
# FILTERS IN SIDEBAR
# =========================================================
st.sidebar.subheader("Dashboard Filters")

date_range = st.sidebar.date_input(
    "Select Date Range",
    []
)

countries = st.sidebar.multiselect(
    "Select Country",
    df["country"].unique()
)

services = st.sidebar.multiselect(
    "Select Service",
    df["service"].unique()
)

traffic = st.sidebar.multiselect(
    "Traffic Source",
    df["traffic_source"].unique()
)

devices = st.sidebar.multiselect(
    "Device Type",
    df["device"].unique()
)

# =========================================================
# APPLY FILTERS
# =========================================================
filtered_df = df.copy()

if len(date_range) == 2:

    filtered_df = filtered_df[
        (filtered_df["timestamp"].dt.date >= date_range[0]) &
        (filtered_df["timestamp"].dt.date <= date_range[1])
    ]

if countries:
    filtered_df = filtered_df[
        filtered_df["country"].isin(countries)
    ]

if services:
    filtered_df = filtered_df[
        filtered_df["service"].isin(services)
    ]

if traffic:
    filtered_df = filtered_df[
        filtered_df["traffic_source"].isin(traffic)
    ]

if devices:
    filtered_df = filtered_df[
        filtered_df["device"].isin(devices)
    ]

# =========================================================
# ROLE-BASED ACCESS
# =========================================================
role = st.session_state.role

if role == "Sales & Marketing":

    allowed_views = [
        "Overview",
        "Sales",
        "Marketing"
    ]

    if view not in allowed_views:
        st.error("Access Denied")
        st.stop()

# =========================================================
# HEADER
# =========================================================
st.title("CyberNova Analytics Dashboard")

st.markdown(
    f"""
    Welcome **{st.session_state.username}**
    """
)

# =========================================================
# KPI SECTION
# =========================================================
st.subheader("Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

total_users = filtered_df["user_id"].nunique()
total_sessions = filtered_df["session_id"].nunique()
conversion_rate = filtered_df["converted"].mean() * 100
avg_time = filtered_df["time_spent"].mean()

col1.metric("Total Users", total_users)
col2.metric("Sessions", total_sessions)
col3.metric("Conversion Rate (%)", f"{conversion_rate:.2f}")
col4.metric("Avg Time Spent (s)", f"{avg_time:.1f}")

# =========================================================
# OVERVIEW DASHBOARD
# =========================================================
if view == "Overview":

    st.subheader("Engagement Over Time")

    time_series = filtered_df.groupby(
        filtered_df["timestamp"].dt.date
    ).size().reset_index(name="interactions")

    fig = px.line(
        time_series,
        x="timestamp",
        y="interactions",
        markers=True
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top Services")

    service_data = (
        filtered_df["service"]
        .value_counts()
        .reset_index()
    )

    service_data.columns = ["service", "count"]

    fig = px.bar(
        service_data,
        x="service",
        y="count",
        text_auto=True
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================================================
# SALES DASHBOARD
# =========================================================
elif view == "Sales":

    st.subheader("Conversion by Traffic Source")

    conversion_data = (
        filtered_df.groupby("traffic_source")["converted"]
        .mean()
        .reset_index()
    )

    fig = px.bar(
        conversion_data,
        x="traffic_source",
        y="converted",
        text_auto=True
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Conversions by Service")

    service_conv = (
        filtered_df.groupby("service")["converted"]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        service_conv,
        x="service",
        y="converted",
        text_auto=True
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================================================
# MARKETING DASHBOARD
# =========================================================
elif view == "Marketing":

    st.subheader("Traffic Source Distribution")

    traffic_data = (
        filtered_df["traffic_source"]
        .value_counts()
        .reset_index()
    )

    traffic_data.columns = ["traffic_source", "count"]

    fig = px.pie(
        traffic_data,
        names="traffic_source",
        values="count"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Device Usage")

    device_data = (
        filtered_df["device"]
        .value_counts()
        .reset_index()
    )

    device_data.columns = ["device", "count"]

    fig = px.bar(
        device_data,
        x="device",
        y="count",
        text_auto=True
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================================================
# GEOGRAPHIC DASHBOARD
# =========================================================
elif view == "Geographic":

    st.subheader("Users by Country")

    country_data = (
        filtered_df["country"]
        .value_counts()
        .reset_index()
    )

    country_data.columns = ["country", "count"]

    fig = px.bar(
        country_data,
        x="country",
        y="count",
        text_auto=True
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Engagement by Country")

    country_engagement = (
        filtered_df.groupby("country")["time_spent"]
        .mean()
        .reset_index()
    )

    fig = px.bar(
        country_engagement,
        x="country",
        y="time_spent",
        text_auto=True
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================================================
# EXPORT SECTION
# =========================================================
st.markdown("---")

st.subheader("Export Data")

st.download_button(
    label="Download Filtered Data",
    data=filtered_df.to_csv(index=False),
    file_name="filtered_data.csv",
    mime="text/csv"
)

# =========================================================
# LOGOUT BUTTON
# =========================================================
st.sidebar.markdown("---")

if st.sidebar.button("Logout"):
    logout()