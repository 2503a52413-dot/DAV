import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Smart City Traffic Dashboard",
    page_icon="🚦",
    layout="wide"
)

# =====================================================
# 2. CUSTOM DESIGN
# =====================================================

st.markdown("""
<style>
.stApp {
    background-color: #f4f7fb;
}
h1 {
    color: #12345a;
}
h2, h3 {
    color: #23476b;
}
[data-testid="stMetric"] {
    background-color: white;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #dce3ed;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# 3. LOAD DATASET
# =====================================================

DATA_PATH = (
    Path(__file__).parent
    / "data"
    / "smart_city_traffic_logistics.csv"
)

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)

    # Convert timestamp
    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        dayfirst=True,
        errors="coerce"
    )

    df = df.dropna(subset=["timestamp"]).copy()

    # Convert numeric columns
    numeric_columns = [
        "vehicle_count",
        "average_speed_kmph",
        "temperature_c",
        "rainfall_mm",
        "delivery_vehicles",
        "deliveries_total",
        "deliveries_completed",
        "deliveries_pending",
        "average_delivery_time_min",
        "distance_travelled_km",
        "fuel_consumption_l",
        "accident_count",
        "parking_availability_pct",
        "traffic_congestion_level",
        "logistics_efficiency_pct"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["date"] = df["timestamp"].dt.date
    df["hour"] = df["timestamp"].dt.hour

    return df


try:
    df = load_data()
except FileNotFoundError:
    st.error(
        "Dataset not found. Place the CSV file inside "
        "the data folder with the correct filename."
    )
    st.stop()
except Exception as error:
    st.error(f"Error loading dataset: {error}")
    st.stop()

# =====================================================
# 4. DASHBOARD HEADER
# =====================================================

st.title("🚦 SMART CITY TRAFFIC & LOGISTICS DASHBOARD")

st.markdown("""
### Hyderabad Smart City Analytics
Monitor traffic conditions, transportation,
logistics efficiency and environmental factors.
""")

st.markdown("---")

# =====================================================
# 5. SIDEBAR FILTERS
# =====================================================

st.sidebar.title("⚙️ Dashboard Filters")

cities = sorted(df["city"].dropna().unique())

selected_city = st.sidebar.multiselect(
    "Select City",
    cities,
    default=cities
)

city_data = df[df["city"].isin(selected_city)]

areas = sorted(city_data["area"].dropna().unique())

selected_area = st.sidebar.multiselect(
    "Select Area",
    areas,
    default=areas
)

density_options = sorted(
    city_data["traffic_density"].dropna().unique()
)

selected_density = st.sidebar.multiselect(
    "Traffic Density",
    density_options,
    default=density_options
)

weather_options = sorted(
    city_data["weather"].dropna().unique()
)

selected_weather = st.sidebar.multiselect(
    "Weather",
    weather_options,
    default=weather_options
)

min_date = df["date"].min()
max_date = df["date"].max()

selected_dates = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# =====================================================
# 6. APPLY FILTERS
# =====================================================

if isinstance(selected_dates, (tuple, list)):
    if len(selected_dates) == 2:
        start_date, end_date = selected_dates
    elif len(selected_dates) == 1:
        start_date = end_date = selected_dates[0]
    else:
        start_date, end_date = min_date, max_date
else:
    start_date = end_date = selected_dates

filtered_df = df[
    (df["city"].isin(selected_city)) &
    (df["area"].isin(selected_area)) &
    (df["traffic_density"].isin(selected_density)) &
    (df["weather"].isin(selected_weather)) &
    (df["date"] >= start_date) &
    (df["date"] <= end_date)
].copy()

if filtered_df.empty:
    st.warning("No records found for the selected filters.")
    st.stop()

# =====================================================
# 7. CALCULATE KEY PERFORMANCE INDICATORS
# =====================================================

total_records = len(filtered_df)

total_vehicles = filtered_df["vehicle_count"].mean()

average_speed = filtered_df["average_speed_kmph"].mean()

average_congestion = filtered_df[
    "traffic_congestion_level"
].mean()

total_deliveries = filtered_df[
    "deliveries_total"
].sum()

completed_deliveries = filtered_df[
    "deliveries_completed"
].sum()

pending_deliveries = filtered_df[
    "deliveries_pending"
].sum()

delivery_rate = (
    completed_deliveries / total_deliveries * 100
    if total_deliveries > 0 else 0
)

logistics_efficiency = filtered_df[
    "logistics_efficiency_pct"
].mean()

total_accidents = filtered_df["accident_count"].sum()

# =====================================================
# 8. KPI CARDS
# =====================================================

st.subheader("📊 Key Performance Indicators")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Total Records",
    f"{total_records:,}"
)

col2.metric(
    "Avg. Vehicle Count",
    f"{total_vehicles:.0f}"
)

col3.metric(
    "Average Speed",
    f"{average_speed:.1f} km/h"
)

col4.metric(
    "Traffic Congestion",
    f"{average_congestion:.1f}%"
)

col5.metric(
    "Delivery Completion",
    f"{delivery_rate:.1f}%"
)

col6, col7, col8 = st.columns(3)

col6.metric(
    "Completed Deliveries",
    f"{completed_deliveries:,.0f}"
)

col7.metric(
    "Pending Deliveries",
    f"{pending_deliveries:,.0f}"
)

col8.metric(
    "Total Accidents",
    f"{total_accidents:,.0f}"
)

st.markdown("---")

# =====================================================
# 9. DASHBOARD TABS
# =====================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Overview",
    "🚗 Traffic Analysis",
    "📦 Logistics Analysis",
    "🌦️ Environment",
    "📋 Dataset"
])

# =====================================================
# TAB 1: OVERVIEW
# =====================================================

with tab1:

    st.subheader("Traffic Overview")

    col1, col2 = st.columns(2)

    with col1:

        area_data = (
            filtered_df.groupby("area", as_index=False)
            .agg(
                vehicle_count=("vehicle_count", "mean")
            )
            .sort_values("vehicle_count", ascending=False)
        )

        fig = px.bar(
            area_data,
            x="area",
            y="vehicle_count",
            color="vehicle_count",
            title="Average Vehicle Count by Area",
            color_continuous_scale="Blues"
        )

        fig.update_layout(
            xaxis_title="Area",
            yaxis_title="Average Vehicles",
            template="plotly_white"
        )

        st.plotly_chart(fig, width="stretch")

    with col2:

        density_data = (
            filtered_df["traffic_density"]
            .value_counts()
            .reset_index()
        )

        density_data.columns = ["Density", "Count"]

        fig = px.pie(
            density_data,
            names="Density",
            values="Count",
            hole=0.45,
            title="Traffic Density Distribution"
        )

        st.plotly_chart(fig, )

    # Daily trend

    daily_data = (
        filtered_df.groupby("date", as_index=False)
        .agg(
            congestion=("traffic_congestion_level", "mean"),
            speed=("average_speed_kmph", "mean")
        )
    )

    fig = px.line(
        daily_data,
        x="date",
        y="congestion",
        markers=True,
        title="Daily Average Traffic Congestion",
        labels={
            "date": "Date",
            "congestion": "Congestion (%)"
        }
    )

    fig.update_layout(template="plotly_white")

    st.plotly_chart(fig, )

    st.subheader("Project Summary")

    st.write(
        f"Average logistics efficiency: "
        f"{logistics_efficiency:.2f}%"
    )

    st.write(
        f"Average delivery time: "
        f"{filtered_df['average_delivery_time_min'].mean():.2f} minutes"
    )

# =====================================================
# TAB 2: TRAFFIC ANALYSIS
# =====================================================

with tab2:

    st.subheader("🚗 Traffic Analysis")

    col1, col2 = st.columns(2)

    with col1:

        fig = px.scatter(
            filtered_df,
            x="vehicle_count",
            y="average_speed_kmph",
            color="traffic_density",
            size="traffic_congestion_level",
            hover_data=["area"],
            title="Vehicle Count vs Average Speed"
        )

        st.plotly_chart(fig, )

    with col2:

        congestion_data = (
            filtered_df.groupby("area", as_index=False)
            ["traffic_congestion_level"].mean()
        )

        fig = px.bar(
            congestion_data,
            x="area",
            y="traffic_congestion_level",
            color="traffic_congestion_level",
            title="Traffic Congestion by Area",
            color_continuous_scale="Reds"
        )

        st.plotly_chart(fig, )

    # Hourly traffic pattern

    hourly_data = (
        filtered_df.groupby("hour", as_index=False)
        .agg(
            vehicles=("vehicle_count", "mean"),
            congestion=("traffic_congestion_level", "mean")
        )
    )

    fig = px.line(
        hourly_data,
        x="hour",
        y="vehicles",
        markers=True,
        title="Hourly Average Vehicle Count",
        labels={
            "hour": "Hour of Day",
            "vehicles": "Average Vehicles"
        }
    )

    fig.update_layout(
        template="plotly_white",
        xaxis=dict(dtick=1)
    )

    st.plotly_chart(fig, )

    # Traffic signal analysis

    signal_data = (
        filtered_df["traffic_signal_status"]
        .value_counts()
        .reset_index()
    )

    signal_data.columns = ["Signal Status", "Count"]

    fig = px.pie(
        signal_data,
        names="Signal Status",
        values="Count",
        title="Traffic Signal Status"
    )

    st.plotly_chart(fig, )

# =====================================================
# TAB 3: LOGISTICS ANALYSIS
# =====================================================

with tab3:

    st.subheader("📦 Logistics Performance")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Logistics Efficiency",
        f"{logistics_efficiency:.1f}%"
    )

    col2.metric(
        "Average Delivery Time",
        f"{filtered_df['average_delivery_time_min'].mean():.1f} min"
    )

    col3.metric(
        "Delivery Completion Rate",
        f"{delivery_rate:.1f}%"
    )

    col1, col2 = st.columns(2)

    with col1:

        delivery_data = (
            filtered_df.groupby("area", as_index=False)
            .agg(
                completed=("deliveries_completed", "sum"),
                pending=("deliveries_pending", "sum")
            )
        )

        delivery_long = delivery_data.melt(
            id_vars="area",
            var_name="Status",
            value_name="Deliveries"
        )

        fig = px.bar(
            delivery_long,
            x="area",
            y="Deliveries",
            color="Status",
            barmode="group",
            title="Completed vs Pending Deliveries"
        )

        st.plotly_chart(fig, )

    with col2:

        fig = px.scatter(
            filtered_df,
            x="average_delivery_time_min",
            y="logistics_efficiency_pct",
            color="traffic_density",
            size="deliveries_total",
            hover_data=["area"],
            title="Delivery Time vs Logistics Efficiency"
        )

        st.plotly_chart(fig, )

    daily_delivery = (
        filtered_df.groupby("date", as_index=False)
        .agg(
            completed=("deliveries_completed", "sum"),
            pending=("deliveries_pending", "sum")
        )
    )

    fig = px.line(
        daily_delivery,
        x="date",
        y=["completed", "pending"],
        markers=True,
        title="Daily Delivery Performance"
    )

    st.plotly_chart(fig, )

# =====================================================
# TAB 4: ENVIRONMENT ANALYSIS
# =====================================================

with tab4:

    st.subheader("🌦️ Environmental Analysis")

    col1, col2 = st.columns(2)

    with col1:

        weather_data = (
            filtered_df.groupby("weather", as_index=False)
            ["traffic_congestion_level"].mean()
        )

        fig = px.bar(
            weather_data,
            x="weather",
            y="traffic_congestion_level",
            color="traffic_congestion_level",
            title="Traffic Congestion by Weather",
            color_continuous_scale="Blues"
        )

        st.plotly_chart(fig, )

    with col2:

        fig = px.scatter(
            filtered_df,
            x="rainfall_mm",
            y="traffic_congestion_level",
            color="weather",
            size="vehicle_count",
            hover_data=["area"],
            title="Rainfall vs Traffic Congestion"
        )

        st.plotly_chart(fig, )

    # Road condition analysis

    road_data = (
        filtered_df.groupby("road_condition", as_index=False)
        .agg(
            records=("area", "size"),
            average_speed=("average_speed_kmph", "mean")
        )
    )

    fig = px.bar(
        road_data,
        x="road_condition",
        y="records",
        color="average_speed",
        title="Records by Road Condition",
        color_continuous_scale="Greens"
    )

    st.plotly_chart(fig, )

    # Parking availability

    parking_data = (
        filtered_df.groupby("area", as_index=False)
        ["parking_availability_pct"].mean()
    )

    fig = px.bar(
        parking_data,
        x="area",
        y="parking_availability_pct",
        color="parking_availability_pct",
        title="Parking Availability by Area"
    )

    st.plotly_chart(fig, )

# =====================================================
# TAB 5: DATASET VIEW
# =====================================================

with tab5:

    st.subheader("📋 Project Dataset")

    st.write(
        f"Total records: {len(filtered_df)}"
    )

    search = st.text_input(
        "Search dataset",
        placeholder="Enter an area, city, weather condition..."
    )

    display_df = filtered_df.copy()

    if search:
        mask = display_df.astype(str).apply(
            lambda col: col.str.contains(
                search,
                case=False,
                na=False
            )
        ).any(axis=1)

        display_df = display_df[mask]

    st.dataframe(
        display_df,
        hide_index=True
    )

    csv_data = display_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇️ Download Filtered Dataset",
        data=csv_data,
        file_name="smart_city_filtered_data.csv",
        mime="text/csv"
    )

# =====================================================
# 10. FOOTER
# =====================================================

st.markdown("---")

st.markdown("""
<center>
<h4>SMART CITY TRAFFIC & LOGISTICS MANAGEMENT</h4>
<p>Python | Streamlit | Pandas | Plotly</p>
<p>Project Analytics Dashboard</p>
</center>
""", unsafe_allow_html=True)