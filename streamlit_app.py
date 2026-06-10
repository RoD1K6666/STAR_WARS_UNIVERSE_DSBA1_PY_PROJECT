import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import streamlit as st
from scipy.stats import pearsonr

st.set_page_config(page_title="Star Wars Universe", layout="wide", page_icon="✦")

# ── Plotly template ───────────────────────────────────────────────────────────
PLOTLY_TEMPLATE = dict(
    layout=go.Layout(
        paper_bgcolor="#131318",
        plot_bgcolor="#131318",
        font=dict(color="#c7c7d0", family="Barlow, sans-serif", size=13),
        title=dict(font=dict(family="Barlow Condensed, sans-serif", size=18, color="#e8e8ec")),
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)", linecolor="rgba(255,255,255,0.15)", zeroline=False),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)", linecolor="rgba(255,255,255,0.15)", zeroline=False),
        colorway=["#ffe81f", "#5b9bd5", "#d9685f", "#9b7bd4", "#76b376", "#e0a35a"],
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
)

# ── Matplotlib ────────────────────────────────────────────────────────────────
plt.style.use("dark_background")
plt.rcParams.update({
    "figure.facecolor": "#131318", "axes.facecolor": "#131318",
    "axes.edgecolor": "#3a3a42", "axes.labelcolor": "#c7c7d0",
    "xtick.color": "#c7c7d0", "ytick.color": "#c7c7d0",
    "text.color": "#c7c7d0", "grid.color": "#23232b", "grid.alpha": 0.6,
})

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow:wght@300;400;500;600&family=Barlow+Condensed:wght@500;600;700&display=swap');

:root {
    --bg:#0a0a0d; --panel:#131318;
    --line:rgba(255,255,255,0.08); --line-2:rgba(255,255,255,0.15);
    --text:#e8e8ec; --muted:#8b8b96; --accent:#ffe81f;
}

html, body, [class*="css"] { font-family:'Barlow', sans-serif; }

.stApp { background:var(--bg); }
.block-container { max-width:1120px; padding-top:2.2rem; }

/* Sidebar */
[data-testid="stSidebar"] { background:#0d0d11; border-right:1px solid var(--line); }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] .sw-side-title {
    font-family:'Barlow Condensed',sans-serif; font-weight:700;
    text-transform:uppercase; letter-spacing:.14em;
    color:var(--accent); font-size:1.15rem; margin:0 0 .2rem;
}
[data-testid="stSidebar"] .sw-side-sub {
    color:var(--muted); font-size:.72rem; letter-spacing:.18em;
    text-transform:uppercase; margin-bottom:1.2rem;
}
[data-testid="stSidebar"] label { color:#bfbfca !important; font-size:.92rem !important; }

/* Headings */
h1 {
    font-family:'Barlow Condensed',sans-serif !important; font-weight:700 !important;
    text-transform:uppercase; letter-spacing:.03em; color:var(--text) !important;
}
h2 {
    font-family:'Barlow Condensed',sans-serif !important; font-weight:600 !important;
    text-transform:uppercase; letter-spacing:.05em; color:var(--text) !important;
    border-bottom:1px solid var(--line); padding-bottom:.4rem; margin-top:1.4rem !important;
}
h3 {
    font-family:'Barlow Condensed',sans-serif !important; font-weight:600 !important;
    text-transform:uppercase; letter-spacing:.07em; color:var(--muted) !important;
    font-size:1.02rem !important; margin-top:1.2rem !important;
}

p, li { color:#c7c7d0; line-height:1.7; font-size:.95rem; }
strong { color:var(--text) !important; font-weight:600; }

/* Metric */
[data-testid="metric-container"] {
    background:var(--panel); border:1px solid var(--line);
    border-radius:6px; padding:14px 16px;
}
[data-testid="metric-container"] label {
    color:var(--muted) !important; text-transform:uppercase;
    letter-spacing:.08em; font-size:.68rem !important; font-weight:500 !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color:var(--text) !important; font-family:'Barlow Condensed',sans-serif !important;
    font-weight:700; font-size:1.9rem !important;
}

/* Dataframe / expander */
[data-testid="stDataFrame"] { border:1px solid var(--line) !important; border-radius:6px; }
[data-testid="stExpander"] { border:1px solid var(--line) !important; border-radius:6px; background:var(--panel); }
details summary {
    font-family:'Barlow Condensed',sans-serif !important; text-transform:uppercase;
    letter-spacing:.04em; color:var(--text) !important; font-size:.92rem !important;
}

/* Divider */
hr { border:none !important; border-top:1px solid var(--line) !important; margin:2rem 0 !important; }

/* Text input */
[data-testid="stTextInput"] input {
    background:var(--panel) !important; border:1px solid var(--line-2) !important;
    color:var(--text) !important; border-radius:6px !important; font-family:'Barlow',sans-serif !important;
}
[data-testid="stTextInput"] input:focus { border-color:var(--accent) !important; box-shadow:none !important; }

/* Hero */
.sw-hero { padding:6px 0 26px; border-bottom:1px solid var(--line); margin-bottom:26px; }
.sw-hero .kicker { color:var(--muted); text-transform:uppercase; letter-spacing:.24em; font-size:.72rem; margin-bottom:12px; }
.sw-hero .title {
    font-family:'Barlow Condensed',sans-serif; font-weight:700; font-size:3.6rem;
    line-height:.95; letter-spacing:.02em; color:var(--accent); margin:0;
}
.sw-hero .byline { color:#b9b9c4; font-size:.95rem; margin-top:14px; letter-spacing:.03em; }
.sw-stats { display:flex; gap:42px; margin-top:26px; flex-wrap:wrap; }
.sw-stats > div { display:flex; flex-direction:column; }
.sw-stats .num { font-family:'Barlow Condensed',sans-serif; font-weight:700; font-size:2rem; color:var(--text); line-height:1; }
.sw-stats .lab { color:var(--muted); text-transform:uppercase; letter-spacing:.12em; font-size:.66rem; margin-top:5px; }

/* Card */
.sw-card {
    background:var(--panel); border:1px solid var(--line);
    border-left:2px solid var(--accent); border-radius:4px;
    padding:12px 16px; margin-bottom:8px;
}
.sw-card .name {
    font-family:'Barlow Condensed',sans-serif; font-weight:600;
    text-transform:uppercase; letter-spacing:.03em; color:var(--text); font-size:1.02rem;
}
.sw-card .meta { color:var(--muted); font-size:.82rem; margin-top:2px; }
.sw-card .stat { color:#b9b9c4; font-size:.84rem; margin-top:5px; }

/* Abstract */
.sw-kicker { color:var(--accent); text-transform:uppercase; letter-spacing:.22em; font-size:.74rem; margin-bottom:18px; }
.sw-lead { font-size:1.12rem; line-height:1.75; color:#dadae2; }
.sw-authors {
    font-family:'Barlow Condensed',sans-serif; text-transform:uppercase; letter-spacing:.08em;
    color:var(--accent); font-size:1.15rem; margin-top:22px;
}

/* Scrollbar */
::-webkit-scrollbar { width:9px; }
::-webkit-scrollbar-track { background:transparent; }
::-webkit-scrollbar-thumb { background:#2b2b33; border-radius:5px; }
::-webkit-scrollbar-thumb:hover { background:#3a3a44; }
</style>
""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────
DATA_DIR = "archive/csv"

@st.cache_data
def load_data():
    characters = pd.read_csv(f"{DATA_DIR}/characters.csv")
    planets    = pd.read_csv(f"{DATA_DIR}/planets.csv")
    starships  = pd.read_csv(f"{DATA_DIR}/starships.csv")
    species    = pd.read_csv(f"{DATA_DIR}/species.csv")
    weapons    = pd.read_csv(f"{DATA_DIR}/weapons.csv")
    return characters, planets, starships, species, weapons

characters, planets, starships, species, weapons = load_data()
characters_clean = characters.dropna(subset=["height","weight"]).copy()
starships_clean  = starships.dropna(subset=["length","crew","MGLT"]).copy()
planets_clean    = planets.dropna(subset=["diameter","population"]).copy()
characters_clean["bmi"] = characters_clean["weight"] / characters_clean["height"]**2
starships_clean["passengers_per_meter"] = starships_clean["passengers"] / starships_clean["length"]

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.markdown(
    '<div class="sw-side-title">Star Wars</div>'
    '<div class="sw-side-sub">Data Analysis</div>',
    unsafe_allow_html=True)
section = st.sidebar.radio("Section", [
    "1. Abstract", "2. Dataset Description", "3. Descriptive Statistics",
    "4. Data Cleanup", "5. Plots", "6. Detailed Overview",
    "7. Data Transformation", "8. Hypothesis Check", "9. Discussion",
], label_visibility="collapsed")

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="sw-hero">
    <div class="kicker">Exploratory Data Analysis &nbsp;·&nbsp; DSBA &nbsp;·&nbsp; HSE</div>
    <div class="title">Star Wars Universe</div>
    <div class="byline">Tiniakov Rodion &nbsp;·&nbsp; Belousov Zakhar</div>
    <div class="sw-stats">
        <div><span class="num">{characters.shape[0]}</span><span class="lab">Characters</span></div>
        <div><span class="num">{starships.shape[0]}</span><span class="lab">Starships</span></div>
        <div><span class="num">{weapons.shape[0]}</span><span class="lab">Weapons</span></div>
        <div><span class="num">{planets.shape[0]}</span><span class="lab">Planets</span></div>
        <div><span class="num">{species.shape[0]}</span><span class="lab">Species</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── 1. Abstract ───────────────────────────────────────────────────────────────
if section == "1. Abstract":
    st.header("1. Abstract")

    st.markdown('<div class="sw-kicker">A long time ago in a galaxy far, far away…</div>',
                unsafe_allow_html=True)
    st.markdown("""
<p class="sw-lead">
This project presents an exploratory data analysis of the <strong>Star Wars universe</strong>
dataset, covering characters, starships, planets, species, and weapons.
</p>
""", unsafe_allow_html=True)
    st.write("""
The goal is to find patterns in the physical characteristics of characters, the technical
parameters of starships, and the relationships between variables across tables. The dataset is
composite — several interconnected CSV tables obtained from Kaggle — so part of the work is
joining and reconciling them into a clean analytical base.

The analysis proceeds through descriptive statistics, data cleanup, visualisation, feature
engineering, and two formal hypothesis checks, ending with a discussion of the findings and
their limitations.
""")
    st.markdown('<div class="sw-authors">Tiniakov Rodion &nbsp;·&nbsp; Belousov Zakhar</div>',
                unsafe_allow_html=True)

# ── 2. Dataset Description ────────────────────────────────────────────────────
elif section == "2. Dataset Description":
    st.header("2. Dataset Description")

    search = st.text_input("Search characters by name or species", placeholder="e.g. Luke, Human, Wookiee…")
    if search:
        results = characters[
            characters["name"].str.contains(search, case=False, na=False) |
            characters["species"].str.contains(search, case=False, na=False)
        ]
        st.write(f"Found **{len(results)}** results")
        for _, row in results.iterrows():
            h = f"{row['height']:.2f} m" if pd.notna(row.get("height")) else "—"
            w = f"{row['weight']:.0f} kg" if pd.notna(row.get("weight")) else "—"
            sp = row.get("species","—") if pd.notna(row.get("species")) else "—"
            gn = row.get("gender","—")  if pd.notna(row.get("gender"))  else "—"
            hw = row.get("homeworld","—") if pd.notna(row.get("homeworld")) else "—"
            st.markdown(f"""
<div class="sw-card">
    <div class="name">{row['name']}</div>
    <div class="meta">{sp} &nbsp;·&nbsp; {gn} &nbsp;·&nbsp; {hw}</div>
    <div class="stat">Height {h} &nbsp;|&nbsp; Weight {w}</div>
</div>""", unsafe_allow_html=True)
        st.divider()

    st.write("""
    The dataset covers the Star Wars fictional universe and consists of **5 main tables**:
    - **characters.csv** — physical and biographical data
    - **planets.csv** — astronomical and geographical data
    - **starships.csv** — technical specifications
    - **species.csv** — biological characteristics
    - **weapons.csv** — specifications
    """)

    for name, df in [("characters", characters), ("planets", planets),
                     ("starships", starships), ("species", species), ("weapons", weapons)]:
        with st.expander(f"{name.upper()} — {df.shape[0]} rows × {df.shape[1]} columns"):
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Data types**")
                st.dataframe(df.dtypes.rename("dtype").to_frame())
            with col2:
                missing = df.isnull().sum()
                missing = missing[missing > 0]
                st.write("**Missing values**")
                if missing.empty:
                    st.success("No missing values")
                else:
                    st.dataframe(missing.rename("missing").to_frame())

# ── 3. Descriptive Statistics ─────────────────────────────────────────────────
elif section == "3. Descriptive Statistics":
    st.header("3. Descriptive Statistics")
    st.write("Mean, median, and standard deviation for key numerical fields.")

    fields = {
        "characters": ["height","weight"],
        "planets":    ["diameter","population","orbital_period"],
        "starships":  ["length","crew","MGLT"],
        "species":    ["average_height","average_lifespan"],
    }
    dfs = {"characters":characters,"planets":planets,"starships":starships,"species":species}

    for table, cols in fields.items():
        st.subheader(table.upper())
        rows = []
        for col in cols:
            s = dfs[table][col].dropna()
            rows.append({"field":col,"mean":round(s.mean(),2),"median":round(s.median(),2),
                         "std":round(s.std(),2),"min":round(s.min(),2),"max":round(s.max(),2)})
        st.dataframe(pd.DataFrame(rows).set_index("field"))

# ── 4. Data Cleanup ───────────────────────────────────────────────────────────
elif section == "4. Data Cleanup":
    st.header("4. Data Cleanup")
    st.write("Rows with missing values in key numerical columns were removed.")

    col1,col2,col3 = st.columns(3)
    col1.metric("Characters before", characters.shape[0])
    col1.metric("Characters after",  characters_clean.shape[0])
    col2.metric("Starships before",  starships.shape[0])
    col2.metric("Starships after",   starships_clean.shape[0])
    col3.metric("Planets before",    planets.shape[0])
    col3.metric("Planets after",     planets_clean.shape[0])

    st.subheader("Characters dtypes after cleanup")
    st.dataframe(characters_clean.dtypes.rename("dtype").to_frame())
    st.subheader("Starships dtypes after cleanup")
    st.dataframe(starships_clean.dtypes.rename("dtype").to_frame())

# ── 5. Plots ──────────────────────────────────────────────────────────────────
elif section == "5. Plots":
    st.header("5. Plots for Numerical Fields")

    st.subheader("Histograms")
    col1, col2 = st.columns(2)
    with col1:
        fig = px.histogram(characters_clean, x="height", nbins=15,
                           title="Distribution of Character Height",
                           labels={"height":"Height (m)"}, template=PLOTLY_TEMPLATE,
                           color_discrete_sequence=["#5b9bd5"])
        fig.update_traces(marker_line_color="#131318", marker_line_width=1)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.histogram(starships_clean, x="length", nbins=15,
                           title="Distribution of Starship Length",
                           labels={"length":"Length (m)"}, template=PLOTLY_TEMPLATE,
                           color_discrete_sequence=["#d9685f"])
        fig.update_traces(marker_line_color="#131318", marker_line_width=1)
        st.plotly_chart(fig, use_container_width=True)
    st.write("Height is roughly bell-shaped (~1.80 m). Starship length is heavily right-skewed — most ships under 100 m, with the Executor (19,000 m) as extreme outlier.")

    st.subheader("Scatter: Height vs Weight")
    fig = px.scatter(characters_clean, x="height", y="weight", hover_name="name",
                     color="species", title="Character Height vs Weight",
                     labels={"height":"Height (m)","weight":"Weight (kg)"},
                     template=PLOTLY_TEMPLATE)
    fig.update_traces(marker=dict(size=9, line=dict(width=1, color="#131318")))
    st.plotly_chart(fig, use_container_width=True)
    st.write("Positive correlation between height and weight. Hover over points to see character names.")

    st.subheader("Bar: Average Height by Species")
    top_sp = characters_clean["species"].value_counts().head(6).index
    avg_h  = (characters_clean[characters_clean["species"].isin(top_sp)]
              .groupby("species")["height"].mean().sort_values().reset_index())
    fig = px.bar(avg_h, x="species", y="height",
                 title="Average Height by Species (Top 6)",
                 labels={"height":"Avg Height (m)","species":"Species"},
                 template=PLOTLY_TEMPLATE, color="height",
                 color_continuous_scale=["#23232b","#5b9bd5","#ffe81f"])
    st.plotly_chart(fig, use_container_width=True)
    st.write("Wookiees are the tallest (~2.28 m). Humans cluster near the mean of ~1.78 m.")

# ── 6. Detailed Overview ──────────────────────────────────────────────────────
elif section == "6. Detailed Overview":
    st.header("6. Detailed Overview")

    st.subheader("Height Distribution by Gender")
    fig = px.box(characters_clean, x="gender", y="height", color="gender",
                 title="Height Distribution by Gender",
                 labels={"height":"Height (m)","gender":"Gender"},
                 template=PLOTLY_TEMPLATE,
                 color_discrete_map={"Male":"#5b9bd5","Female":"#d9685f","unknown":"#9b7bd4"})
    st.plotly_chart(fig, use_container_width=True)
    st.write("Male characters have a higher median height (~1.83 m) vs female (~1.70 m) with greater variability.")

    st.subheader("Average Weight by Species (Top 5)")
    top5 = characters_clean["species"].value_counts().head(5).index
    avg_w = (characters_clean[characters_clean["species"].isin(top5)]
             .groupby("species")["weight"].mean().sort_values().reset_index())
    fig = px.bar(avg_w, x="species", y="weight",
                 title="Average Weight by Species (Top 5)",
                 labels={"weight":"Avg Weight (kg)","species":"Species"},
                 template=PLOTLY_TEMPLATE, color="weight",
                 color_continuous_scale=["#23232b","#d9685f","#ffe81f"])
    st.plotly_chart(fig, use_container_width=True)
    st.write("Weight mirrors height trends. High overall std (~149 kg) driven by extreme outliers.")

    st.subheader("Starship Length vs Crew Size by Class")
    fig = px.scatter(starships_clean, x="length", y="crew", color="starship_class",
                     hover_name="name", title="Starship Length vs Crew Size",
                     labels={"length":"Length (m)","crew":"Crew Size"},
                     template=PLOTLY_TEMPLATE)
    fig.update_traces(marker=dict(size=10, line=dict(width=1, color="#131318")))
    st.plotly_chart(fig, use_container_width=True)
    st.write("Larger ships require more crew. The Executor (19,000 m, ~279,000 crew) is an extreme outlier.")

    st.subheader("Planet Diameter and Population")
    col1, col2 = st.columns(2)
    with col1:
        pdf = planets_clean.sort_values("diameter")
        fig = px.bar(pdf, x=pdf.index.astype(str), y="diameter", hover_name="name",
                     title="Planet Diameter", labels={"diameter":"Diameter (km)"},
                     template=PLOTLY_TEMPLATE, color_discrete_sequence=["#5b9bd5"])
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        pdf2 = planets_clean.sort_values("population")
        fig = px.bar(pdf2, x=pdf2.index.astype(str), y="population", hover_name="name",
                     title="Planet Population", labels={"population":"Population"},
                     template=PLOTLY_TEMPLATE, color_discrete_sequence=["#d9685f"])
        st.plotly_chart(fig, use_container_width=True)
    st.write("Diameters similar (10,000–13,000 km). Population varies enormously — one planet near 1 trillion.")

    st.subheader("Correlation Heatmap")
    col1, col2 = st.columns(2)
    chars_tmp = characters_clean.copy()
    chars_tmp["bmi"] = chars_tmp["weight"] / chars_tmp["height"]**2
    with col1:
        corr = chars_tmp[["height","weight","bmi"]].corr()
        fig = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r",
                        title="Characters: Correlation Matrix", template=PLOTLY_TEMPLATE,
                        zmin=-1, zmax=1)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        ship_cols = ["length","crew","MGLT","passengers","cargo_capacity","hyperdrive_rating"]
        corr2 = starships_clean[ship_cols].corr()
        fig = px.imshow(corr2, text_auto=".2f", color_continuous_scale="RdBu_r",
                        title="Starships: Correlation Matrix", template=PLOTLY_TEMPLATE,
                        zmin=-1, zmax=1)
        st.plotly_chart(fig, use_container_width=True)
    st.write("Characters: height/weight moderately correlated; BMI negatively with height. Starships: length, crew, passengers, cargo strongly correlated. MGLT weakly negative with length.")

    st.subheader("Weapons Analysis")
    weapons_clean = weapons.dropna(subset=["type"])
    col1, col2, col3 = st.columns(3)
    with col1:
        wc = weapons_clean["type"].value_counts().reset_index()
        fig = px.bar(wc, x="type", y="count", title="Weapon Count by Type",
                     template=PLOTLY_TEMPLATE, color_discrete_sequence=["#5b9bd5"])
        fig.update_layout(xaxis_tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        wca = (weapons_clean.dropna(subset=["cost_in_credits"])
               .groupby("type")["cost_in_credits"].mean().sort_values().reset_index())
        fig = px.bar(wca, x="type", y="cost_in_credits", title="Avg Cost by Type",
                     template=PLOTLY_TEMPLATE, color_discrete_sequence=["#d9685f"])
        fig.update_layout(xaxis_tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    with col3:
        wla = (weapons_clean.dropna(subset=["length"])
               .groupby("type")["length"].mean().sort_values().reset_index())
        fig = px.bar(wla, x="type", y="length", title="Avg Length by Type",
                     template=PLOTLY_TEMPLATE, color_discrete_sequence=["#9b7bd4"])
        fig.update_layout(xaxis_tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    st.write("Blasters are most common. Missile weapons most expensive. Lightsabers notably compact.")

# ── 7. Data Transformation ────────────────────────────────────────────────────
elif section == "7. Data Transformation":
    st.header("7. Data Transformation")

    st.subheader("BMI for Characters")
    st.write("BMI = weight / height² — allows comparing body composition across species.")

    col1, col2 = st.columns(2)
    with col1:
        st.write("**Highest BMI**")
        for _, row in characters_clean.nlargest(5,"bmi").iterrows():
            st.markdown(f"""
<div class="sw-card">
    <div class="name">{row['name']}</div>
    <div class="meta">{row.get('species','—')}</div>
    <div class="stat">BMI <strong>{row['bmi']:.1f}</strong>
     &nbsp;|&nbsp; {row['height']:.2f} m &nbsp;/&nbsp; {row['weight']:.0f} kg</div>
</div>""", unsafe_allow_html=True)
    with col2:
        st.write("**Lowest BMI**")
        for _, row in characters_clean.nsmallest(5,"bmi").iterrows():
            st.markdown(f"""
<div class="sw-card">
    <div class="name">{row['name']}</div>
    <div class="meta">{row.get('species','—')}</div>
    <div class="stat">BMI <strong>{row['bmi']:.1f}</strong>
     &nbsp;|&nbsp; {row['height']:.2f} m &nbsp;/&nbsp; {row['weight']:.0f} kg</div>
</div>""", unsafe_allow_html=True)

    st.write("**Full table (first 10 rows)**")
    st.dataframe(characters_clean[["name","species","height","weight","bmi"]].head(10).reset_index(drop=True))

    st.divider()
    st.subheader("Passengers per Meter for Starships")
    st.write("passengers_per_meter = passengers / length — transport efficiency metric.")
    st.dataframe(starships_clean[["name","length","passengers","passengers_per_meter"]].head(10).reset_index(drop=True))
    fig = px.bar(
        starships_clean.dropna(subset=["passengers_per_meter"])
                       .sort_values("passengers_per_meter", ascending=False).head(15),
        x="name", y="passengers_per_meter",
        title="Top 15 Ships by Passengers per Meter",
        labels={"passengers_per_meter":"Passengers/m","name":"Ship"},
        template=PLOTLY_TEMPLATE, color_discrete_sequence=["#ffe81f"]
    )
    fig.update_layout(xaxis_tickangle=45)
    st.plotly_chart(fig, use_container_width=True)

# ── 8. Hypothesis Check ───────────────────────────────────────────────────────
elif section == "8. Hypothesis Check":
    st.header("8. Hypothesis Check")

    st.subheader("Hypothesis 1: Larger starships are slower (lower MGLT)")
    st.write("**Hypothesis:** Ships with greater length have lower MGLT speed.")
    h1 = starships_clean[["name","length","MGLT","starship_class"]].dropna()
    fig = px.scatter(h1, x="length", y="MGLT", hover_name="name",
                     color="starship_class", trendline="ols",
                     title="Starship Length vs MGLT Speed",
                     labels={"length":"Length (m)","MGLT":"MGLT"},
                     template=PLOTLY_TEMPLATE)
    fig.update_traces(marker=dict(size=10, line=dict(width=1, color="#131318")))
    st.plotly_chart(fig, use_container_width=True)
    corr, pval = pearsonr(h1["length"], h1["MGLT"])
    col1,col2,col3 = st.columns(3)
    col1.metric("Pearson r", f"{corr:.3f}")
    col2.metric("p-value",   f"{pval:.4f}")
    col3.metric("Sample size", len(h1))
    st.write("**Result:** r = −0.384 (p = 0.010) — significant but moderate. Hypothesis **partially confirmed**.")

    st.divider()

    st.subheader("Hypothesis 2: Humans have more uniform BMI than non-humans")
    st.write("**Hypothesis:** Human characters have lower BMI standard deviation than non-humans.")
    humans     = characters_clean[characters_clean["species"]=="Human"]["bmi"].dropna()
    non_humans = characters_clean[characters_clean["species"]!="Human"]["bmi"].dropna()
    bmi_df = pd.concat([
        humans.rename("bmi").to_frame().assign(group="Human"),
        non_humans.rename("bmi").to_frame().assign(group="Non-Human")
    ])
    fig = px.box(bmi_df, x="group", y="bmi", color="group",
                 title="BMI Distribution: Humans vs Non-Humans",
                 labels={"bmi":"BMI","group":"Group"},
                 template=PLOTLY_TEMPLATE, points="all",
                 color_discrete_map={"Human":"#5b9bd5","Non-Human":"#d9685f"})
    st.plotly_chart(fig, use_container_width=True)
    stats = pd.DataFrame({
        "Group":  ["Human","Non-Human"],
        "n":      [len(humans), len(non_humans)],
        "mean":   [round(humans.mean(),2), round(non_humans.mean(),2)],
        "std":    [round(humans.std(),2),  round(non_humans.std(),2)],
        "min":    [round(humans.min(),2),  round(non_humans.min(),2)],
        "max":    [round(humans.max(),2),  round(non_humans.max(),2)],
    }).set_index("Group")
    st.dataframe(stats)
    st.write("**Result:** Human BMI std = 2.91 vs non-human std = 13.93 — nearly 5× higher. Hypothesis **confirmed**.")

# ── 9. Discussion ─────────────────────────────────────────────────────────────
elif section == "9. Discussion":
    st.header("9. Discussion")

    for title, body in [
        ("Dataset and data quality",
         "The dataset covers five interconnected tables. Data quality varied — characters lost ~31% of rows after dropping missing height/weight, planets dropped from 26 to 11. All missing values handled by row removal rather than imputation."),
        ("Descriptive statistics",
         "Character heights tightly distributed around 1.80 m (std = 0.38 m). Starship length heavily skewed: median 20.75 m vs mean 604 m. Crew follows the same pattern — median 1, mean 7,344. MGLT most uniform (std = 19.35, range 20–120)."),
        ("Plots and overview",
         "Height near-normally distributed. Height and weight positively correlated with notable outliers. Wookiees are tallest and heaviest. Male characters taller on average with greater variability. Larger ships consistently require more crew. Planet population varies by orders of magnitude."),
        ("Data transformation",
         "BMI falls in a realistic range (16–34) for humanoids. Non-humanoid outliers (Jabba, Yoda) produce extreme values. passengers_per_meter shows combat ships carry zero passengers while large transports achieve 1–2 per meter."),
        ("Hypotheses",
         "Hypothesis 1 partially confirmed: r = −0.384 (p = 0.010), significant but moderate. Length alone does not predict speed.\n\nHypothesis 2 confirmed: Human BMI std (2.91) is nearly 5× lower than non-human (13.93), driven by species with radically different body proportions."),
    ]:
        st.subheader(title)
        st.write(body)
