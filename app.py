import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Black Hole Analytics",
    page_icon="🌀",
    layout="wide"
)

# =====================================================
# CUSTOM FUTURISTIC THEME (GLASS UI)
# =====================================================
st.markdown("""
    <style>
        .stApp {
            background-color: #080C14;
            color: #e6edf7;
        }
        .card {
            background: rgba(18, 27, 45, 0.65);
            padding: 18px;
            border-radius: 14px;
            border: 1px solid rgba(78, 158, 255, 0.25);
            box-shadow: 0px 4px 20px rgba(0,0,0,0.4);
        }
        .kpi {
            background: linear-gradient(135deg, #121B2D, #09101A);
            padding: 20px;
            border-radius: 14px;
            border: 1px solid rgba(78,158,255,0.4);
            text-align: center;
            color: #e6edf7;
            font-size: 18px;
        }
        .metric-value {
            font-size: 26px;
            font-weight: 700;
            color: #4e9eff;
        }
    </style>
""", unsafe_allow_html=True)

# Theme colors
BG = "#080C14"          # background
ACCENT = "#4e9eff"      # electric blue
MAGENTA = "#ff4e88"     # pink accent
PANEL = "#121B2D"       # card color

# =====================================================
# TITLE
# =====================================================
st.markdown(
    "<h2 style='text-align:center;color:#4e9eff;'>🌀 Black Hole Accretion Intelligence System</h2>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align:center;color:#9db4cf;'>Next-Gen Analytical Dashboard • Sci-Fi UI/UX • Fully Dynamic</p>",
    unsafe_allow_html=True
)

# =====================================================
# UPLOAD DATA
# =====================================================
uploaded = st.file_uploader("Upload Black Hole Dataset (.xlsx)", type=["xlsx"])

if uploaded is None:
    st.info("Upload the Excel dataset to generate the dashboard.")
    st.stop()

df = pd.read_excel(uploaded)
df.columns = df.columns.str.strip()

# convert numeric cols
for col in df.columns:
    df[col] = pd.to_numeric(df[col], errors="ignore")

# =====================================================
# CLASSIFICATION LOGIC
# =====================================================
def classify_mass(v):
    try:
        q1, q2 = df["BlackHole_Mass_SolarMass"].quantile([0.33, 0.66])
        if v < q1:
            return "Low Mass"
        elif v < q2:
            return "Medium Mass"
        else:
            return "High Mass"
    except Exception:
        return "Unknown"

def classify_spin(v):
    try:
        if v < 0.33:
            return "Low Spin"
        elif v < 0.66:
            return "Medium Spin"
        else:
            return "High Spin"
    except Exception:
        return "Unknown"

def classify_edd(e):
    try:
        if e < 0.1:
            return "Sub-Eddington"
        elif e <= 1.0:
            return "Near-Eddington"
        else:
            return "Super-Eddington"
    except Exception:
        return "Unknown"

df["Mass_Class"] = df["BlackHole_Mass_SolarMass"].apply(classify_mass)
df["Spin_Class"] = df["Spin_Factor"].apply(classify_spin)
df["Eddington_Class"] = df["Eddington_Ratio"].apply(classify_edd)

# =====================================================
# SIDEBAR FILTERS
# =====================================================
st.sidebar.markdown("<h3 style='color:#4e9eff;'>🔎 Filters</h3>", unsafe_allow_html=True)

mass_f = st.sidebar.multiselect(
    "Mass Category",
    sorted(df["Mass_Class"].unique()),
    sorted(df["Mass_Class"].unique())
)
spin_f = st.sidebar.multiselect(
    "Spin Category",
    sorted(df["Spin_Class"].unique()),
    sorted(df["Spin_Class"].unique())
)
edd_f = st.sidebar.multiselect(
    "Accretion Regime",
    sorted(df["Eddington_Class"].unique()),
    sorted(df["Eddington_Class"].unique())
)

filtered = df[
    df["Mass_Class"].isin(mass_f) &
    df["Spin_Class"].isin(spin_f) &
    df["Eddington_Class"].isin(edd_f)
]

# =====================================================
# KPI BLOCKS (NEW DESIGN)
# =====================================================
k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(
        "<div class='kpi'>Total Objects<br><div class='metric-value'>"
        + str(len(filtered)) + "</div></div>",
        unsafe_allow_html=True
    )

with k2:
    st.markdown(
        "<div class='kpi'>Mean Mass (M☉)<br><div class='metric-value'>"
        + f"{filtered['BlackHole_Mass_SolarMass'].mean():.2f}" + "</div></div>",
        unsafe_allow_html=True
    )

with k3:
    st.markdown(
        "<div class='kpi'>Mean Spin<br><div class='metric-value'>"
        + f"{filtered['Spin_Factor'].mean():.3f}" + "</div></div>",
        unsafe_allow_html=True
    )

with k4:
    st.markdown(
        "<div class='kpi'>Mean X-ray Luminosity<br><div class='metric-value'>"
        + f"{filtered['Xray_Luminosity_erg_s'].mean():.2e}" + "</div></div>",
        unsafe_allow_html=True
    )

st.markdown("")

# =====================================================
# ROW 1 — DONUT + BAR
# =====================================================
r1c1, r1c2 = st.columns(2)

with r1c1:
    fig = px.pie(
        filtered,
        names="Mass_Class",
        hole=0.55,
        color_discrete_sequence=[ACCENT, MAGENTA, "#82eefd"]
    )
    fig.update_layout(
        template="plotly_dark",
        title="Mass Class Breakdown",
        paper_bgcolor=BG
    )
    st.plotly_chart(fig, use_container_width=True)

with r1c2:
    spin_count = filtered["Spin_Class"].value_counts().reset_index()
    spin_count.columns = ["Spin_Class", "count"]

    fig = px.bar(
        spin_count,
        x="Spin_Class",
        y="count",
        color="count",
        color_continuous_scale="Viridis"
    )
    fig.update_layout(
        template="plotly_dark",
        title="Spin Class Distribution",
        paper_bgcolor=BG
    )
    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# ROW 2 — SCATTER + TEMPERATURE LINE
# =====================================================
r2c1, r2c2 = st.columns(2)

with r2c1:
    fig = px.scatter(
        filtered,
        x="BlackHole_Mass_SolarMass",
        y="Xray_Luminosity_erg_s",
        color="Eddington_Class",
        hover_data=["BlackHole_ID"],
        color_discrete_sequence=[ACCENT, MAGENTA, "#ffa94e"]
    )
    fig.update_layout(
        template="plotly_dark",
        title="Mass vs X-ray Luminosity",
        paper_bgcolor=BG
    )
    st.plotly_chart(fig, use_container_width=True)

with r2c2:
    fig = px.line(
        filtered.sort_values("BlackHole_Mass_SolarMass"),
        x="BlackHole_Mass_SolarMass",
        y="Disk_Temperature_Inner_K",
        color_discrete_sequence=[ACCENT],
        template="plotly_dark"
    )
    fig.update_layout(
        title="Inner Disk Temperature Trend",
        paper_bgcolor=BG
    )
    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# ROW 3 — RADAR + GAUGE
# =====================================================
r3c1, r3c2 = st.columns(2)

with r3c1:
    radar_cols = [
        "Magnetic_Flux_Gauss", "Gravitational_Redshift",
        "Radiation_Pressure", "Relativistic_Beaming_Factor",
        "Hardness_Ratio", "Eddington_Ratio"
    ]
    radar_vals = [filtered[c].mean() if c in filtered else 0 for c in radar_cols]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=radar_vals,
        theta=radar_cols,
        fill='toself',
        line_color=ACCENT
    ))
    fig.update_layout(
        title="Accretion Physics Radar Model",
        template="plotly_dark",
        paper_bgcolor=BG
    )
    st.plotly_chart(fig, use_container_width=True)

with r3c2:
    # Jet power gauge
    if "Jet_Energy_erg" in filtered and not filtered["Jet_Energy_erg"].isna().all():
        jet_mean = filtered["Jet_Energy_erg"].mean()
        jet_90 = df["Jet_Energy_erg"].quantile(0.90)
        score = min(100, (jet_mean / jet_90) * 100) if jet_90 else 0
    else:
        score = 0

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={"text": "Jet Power Index"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": MAGENTA}
        }
    ))
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=BG
    )
    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# TABLE
# =====================================================
with st.expander("Show Filtered Data Table"):
    st.dataframe(filtered)
