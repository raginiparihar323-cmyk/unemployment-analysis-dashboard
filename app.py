import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Unemployment Analysis Dashboard",
    page_icon="📊",
    layout="wide"
)

# ================= LOAD DATA =================
df = pd.read_csv("Unemployment in India.csv")
df.columns = df.columns.str.strip()
df = df.dropna()
df["Date"] = pd.to_datetime(df["Date"])

# ================= SIDEBAR =================
st.sidebar.title("📊 Dashboard Controls")

theme = st.sidebar.radio(
    "Choose Theme",
    ["Light", "Dark"]
)

regions = sorted(df["Region"].dropna().unique())
areas = sorted(df["Area"].dropna().unique())

selected_regions = st.sidebar.multiselect(
    "Select State/Region",
    regions,
    default=regions[:5]
)

selected_areas = st.sidebar.multiselect(
    "Select Area",
    areas,
    default=areas
)

filtered_df = df[
    (df["Region"].isin(selected_regions)) &
    (df["Area"].isin(selected_areas))
]

if filtered_df.empty:
    st.warning("Please select at least one state and one area.")
    st.stop()

# ================= THEME =================
if theme == "Dark":
    template = "plotly_dark"
else:
    template = "plotly_white"

# ================= HEADER =================
st.title("📊 Unemployment Analysis Dashboard")
st.markdown("### Analyze unemployment trends, COVID-19 impact, state-wise patterns and labour participation")

# ================= METRICS =================
avg_unemployment = filtered_df["Estimated Unemployment Rate (%)"].mean()
max_unemployment = filtered_df["Estimated Unemployment Rate (%)"].max()
avg_labour = filtered_df["Estimated Labour Participation Rate (%)"].mean()
total_records = filtered_df.shape[0]

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("📉 Avg Unemployment", f"{avg_unemployment:.2f}%")

with c2:
    st.metric("⚠️ Max Unemployment", f"{max_unemployment:.2f}%")

with c3:
    st.metric("👥 Labour Participation", f"{avg_labour:.2f}%")

with c4:
    st.metric("📁 Total Records", total_records)

st.write("---")

# ================= INSIGHTS =================
state_avg = (
    filtered_df.groupby("Region")["Estimated Unemployment Rate (%)"]
    .mean()
    .reset_index()
    .sort_values(by="Estimated Unemployment Rate (%)", ascending=False)
)

highest_state = state_avg.iloc[0]["Region"]
highest_value = state_avg.iloc[0]["Estimated Unemployment Rate (%)"]

lowest_state = state_avg.iloc[-1]["Region"]
lowest_value = state_avg.iloc[-1]["Estimated Unemployment Rate (%)"]

st.success(
    f"💡 Key Insight: {highest_state} has the highest average unemployment rate "
    f"({highest_value:.2f}%), while {lowest_state} has the lowest average unemployment rate "
    f"({lowest_value:.2f}%) among selected regions."
)

# ================= TABS =================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Overview",
    "🏙️ State Analysis",
    "🦠 COVID Impact",
    "🏆 Ranking",
    "📁 Dataset"
])

# ================= TAB 1 =================
with tab1:
    st.subheader("📈 Unemployment Trend Over Time")

    fig1 = px.line(
        filtered_df,
        x="Date",
        y="Estimated Unemployment Rate (%)",
        color="Region",
        markers=True,
        title="Unemployment Rate Over Time",
        template=template
    )

    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("👥 Employment vs Unemployment")

    fig2 = px.scatter(
        filtered_df,
        x="Estimated Employed",
        y="Estimated Unemployment Rate (%)",
        color="Region",
        size="Estimated Labour Participation Rate (%)",
        hover_data=["Area", "Date"],
        title="Employment vs Unemployment Rate",
        template=template
    )

    st.plotly_chart(fig2, use_container_width=True)

# ================= TAB 2 =================
with tab2:
    st.subheader("🏙️ State-wise Average Unemployment")

    fig3 = px.bar(
        state_avg,
        x="Region",
        y="Estimated Unemployment Rate (%)",
        color="Estimated Unemployment Rate (%)",
        title="Average Unemployment by State",
        color_continuous_scale="Bluered",
        template=template
    )

    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("🌆 Urban vs Rural Distribution")

    fig4 = px.pie(
        filtered_df,
        names="Area",
        title="Urban vs Rural Data Distribution",
        hole=0.45,
        template=template
    )

    st.plotly_chart(fig4, use_container_width=True)

# ================= TAB 3 =================
with tab3:
    st.subheader("🦠 COVID-19 Impact Analysis")

    covid_df = filtered_df[filtered_df["Date"].dt.year == 2020]

    fig5 = px.line(
        covid_df,
        x="Date",
        y="Estimated Unemployment Rate (%)",
        color="Region",
        markers=True,
        title="Unemployment Trend During COVID-19",
        template=template
    )

    st.plotly_chart(fig5, use_container_width=True)

    before_covid = filtered_df[filtered_df["Date"].dt.year < 2020]["Estimated Unemployment Rate (%)"].mean()
    during_covid = covid_df["Estimated Unemployment Rate (%)"].mean()

    st.info(
        f"Before COVID average unemployment was approximately {before_covid:.2f}%, "
        f"while during 2020 it was approximately {during_covid:.2f}%."
    )

# ================= TAB 4 =================
with tab4:
    st.subheader("🏆 Top States Ranking")

    ranking = state_avg.copy()
    ranking.insert(0, "Rank", range(1, len(ranking) + 1))

    st.dataframe(ranking, use_container_width=True)

    fig6 = px.bar(
        ranking.head(10),
        x="Estimated Unemployment Rate (%)",
        y="Region",
        orientation="h",
        color="Estimated Unemployment Rate (%)",
        title="Top 10 States with Highest Unemployment",
        color_continuous_scale="Reds",
        template=template
    )

    st.plotly_chart(fig6, use_container_width=True)

# ================= TAB 5 =================
with tab5:
    st.subheader("📁 Dataset Preview")

    st.dataframe(filtered_df, use_container_width=True)

    csv = filtered_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇️ Download Filtered Dataset",
        data=csv,
        file_name="filtered_unemployment_data.csv",
        mime="text/csv"
    )

    st.subheader("📌 Dataset Summary")
    st.write(filtered_df.describe())

# ================= FOOTER =================
st.write("---")
st.caption("Made with ❤️ using Python, Streamlit, Pandas and Plotly")