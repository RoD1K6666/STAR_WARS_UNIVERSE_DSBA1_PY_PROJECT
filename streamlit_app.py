import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import streamlit as st
from scipy.stats import pearsonr

st.set_page_config(page_title="Star Wars Universe", layout="wide", page_icon="⭐")

# ── Plotly dark template ──────────────────────────────────────────────────────
PLOTLY_TEMPLATE = dict(
    layout=go.Layout(
        paper_bgcolor="#0d0d20",
        plot_bgcolor="#0d0d20",
        font=dict(color="#e0e0f0", family="Exo 2, sans-serif"),
        xaxis=dict(gridcolor="#1e1e3a", linecolor="#333355"),
        yaxis=dict(gridcolor="#1e1e3a", linecolor="#333355"),
        colorway=["#FFE81F", "#4fc3f7", "#ef5350", "#ab47bc", "#66bb6a", "#ffa726"],
    )
)

# ── Matplotlib dark ───────────────────────────────────────────────────────────
plt.style.use("dark_background")
plt.rcParams.update({
    "figure.facecolor": "#0d0d20", "axes.facecolor": "#0d0d20",
    "axes.edgecolor": "#333355", "axes.labelcolor": "#e0e0f0",
    "xtick.color": "#e0e0f0", "ytick.color": "#e0e0f0",
    "text.color": "#e0e0f0", "grid.color": "#1e1e3a", "grid.alpha": 0.5,
})

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Exo+2:wght@300;400;600&display=swap');

@keyframes pulseGlow {
    0%,100% { text-shadow: 0 0 10px #FFE81F88, 0 0 30px #FFE81F44; }
    50%      { text-shadow: 0 0 25px #FFE81Fff, 0 0 60px #FFE81F99, 0 0 100px #FFE81F44; }
}
@keyframes borderGlow {
    0%,100% { box-shadow: 0 0 8px #FFE81F22, inset 0 0 8px #FFE81F08; }
    50%      { box-shadow: 0 0 22px #FFE81F55, inset 0 0 16px #FFE81F15; }
}
@keyframes fadeInUp {
    from { opacity:0; transform:translateY(18px); }
    to   { opacity:1; transform:translateY(0); }
}
@keyframes crawl {
    0%   { transform: perspective(400px) rotateX(20deg) translateY(30%); }
    100% { transform: perspective(400px) rotateX(20deg) translateY(-200%); }
}
@keyframes flicker {
    0%,100%{opacity:1;} 92%{opacity:1;} 93%{opacity:.7;} 94%{opacity:1;}
}
@keyframes countUp {
    from { opacity:0; transform:scale(.7); }
    to   { opacity:1; transform:scale(1); }
}
@keyframes saberSlide {
    0%   { width:0; opacity:0; }
    30%  { opacity:1; }
    100% { width:100%; opacity:1; }
}
@keyframes typewriter {
    from { width:0; }
    to   { width:100%; }
}

html, body, [class*="css"] { font-family:'Exo 2',sans-serif; }

.stApp {
    background:
        radial-gradient(ellipse at 15% 40%, #0a0a2a 0%, transparent 55%),
        radial-gradient(ellipse at 85% 20%, #0a180a 0%, transparent 50%),
        radial-gradient(ellipse at 50% 85%, #1a0808 0%, transparent 50%),
        #04040f;
}
.stApp::after {
    content:"";
    position:fixed; inset:0;
    background: repeating-linear-gradient(0deg,
        transparent, transparent 2px,
        rgba(0,0,0,0.07) 2px, rgba(0,0,0,0.07) 4px);
    pointer-events:none; z-index:9999;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#02020a 0%,#07071a 50%,#0a0a1f 100%);
    border-right:1px solid #FFE81F44;
    box-shadow:4px 0 20px #FFE81F11;
}
[data-testid="stSidebar"]::before {
    content:"✦  STAR WARS  ✦";
    display:block;
    font-family:'Orbitron',sans-serif; font-weight:900; font-size:.85rem;
    color:#FFE81F;
    animation:pulseGlow 3s ease-in-out infinite;
    letter-spacing:.2em; text-align:center;
    padding:28px 16px 12px; border-bottom:1px solid #FFE81F33; margin-bottom:20px;
}
[data-testid="stSidebar"] p {
    font-family:'Orbitron',sans-serif !important;
    font-size:.65rem !important; color:#FFE81Fbb !important;
    letter-spacing:.15em; text-transform:uppercase;
}
[data-testid="stSidebar"] label {
    font-family:'Exo 2',sans-serif !important;
    color:#b0b0cc !important; font-size:.88rem !important; transition:color .2s;
}
[data-testid="stSidebar"] label:hover { color:#FFE81F !important; }

/* Headings */
h1 {
    font-family:'Orbitron',sans-serif !important; font-weight:900 !important;
    color:#FFE81F !important;
    animation:pulseGlow 4s ease-in-out infinite, flicker 8s infinite;
    letter-spacing:.1em;
}
h2 {
    font-family:'Orbitron',sans-serif !important; font-weight:700 !important;
    color:#FFE81F !important; text-shadow:0 0 12px #FFE81F66;
    padding-bottom:8px; letter-spacing:.06em;
    animation:fadeInUp .5s ease;
    position:relative; overflow:hidden;
}
h2::after {
    content:"";
    position:absolute; bottom:0; left:0; height:2px;
    background:linear-gradient(90deg,#FFE81F,#4fc3f7,#FFE81F);
    animation:saberSlide 1s ease forwards;
}
h3 {
    font-family:'Orbitron',sans-serif !important; font-weight:400 !important;
    color:#a0c0ff !important; letter-spacing:.05em;
}

/* Metric cards */
[data-testid="metric-container"] {
    background:linear-gradient(135deg,#08081a,#10102a);
    border:1px solid #FFE81F44; border-radius:12px; padding:18px;
    animation:borderGlow 3s ease-in-out infinite;
    transition:transform .2s, box-shadow .2s;
}
[data-testid="metric-container"]:hover {
    transform:translateY(-3px);
    box-shadow:0 8px 25px #FFE81F33 !important;
}
[data-testid="metric-container"] label {
    font-family:'Orbitron',sans-serif !important; color:#FFE81F !important;
    font-size:.65rem !important; letter-spacing:.15em; text-transform:uppercase;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color:#fff !important; font-family:'Orbitron',sans-serif !important;
    font-size:1.9rem !important; text-shadow:0 0 10px #ffffff66;
    animation:countUp .6s ease;
}

/* Dataframes */
[data-testid="stDataFrame"] {
    border:1px solid #FFE81F22 !important;
    border-radius:8px; overflow:hidden; box-shadow:0 0 15px #FFE81F0a;
}

/* Expander */
[data-testid="stExpander"] {
    border:1px solid #FFE81F33 !important; border-radius:10px;
    background:linear-gradient(135deg,#08081a,#0d0d20);
    transition:border-color .3s;
}
[data-testid="stExpander"]:hover { border-color:#FFE81F77 !important; }
details summary {
    font-family:'Orbitron',sans-serif !important;
    color:#FFE81F !important; font-size:.82rem !important; letter-spacing:.06em;
}

/* Divider */
hr {
    border:none !important; height:2px !important;
    background:linear-gradient(90deg,transparent,#FFE81F,#4fc3f7,#FFE81F,transparent) !important;
    margin:2.5em 0 !important; box-shadow:0 0 10px #FFE81F55;
    animation:saberSlide 1.2s ease;
}

/* Text */
p,li { color:#c8c8e0; line-height:1.8; }
strong { color:#FFE81F !important; }

/* Character card */
.char-card {
    background:linear-gradient(135deg,#08081e,#0f0f28);
    border:1px solid #FFE81F33; border-radius:10px;
    padding:16px 18px; margin-bottom:10px;
    transition:transform .2s, border-color .2s, box-shadow .2s;
    animation:fadeInUp .4s ease;
}
.char-card:hover {
    transform:translateY(-3px);
    border-color:#FFE81Faa;
    box-shadow:0 6px 20px #FFE81F22;
}
.char-name {
    font-family:'Orbitron',sans-serif; font-weight:700;
    color:#FFE81F; font-size:.95rem; letter-spacing:.05em; margin-bottom:6px;
}
.char-meta { color:#8888aa; font-size:.8rem; }
.char-stat { color:#a0c0ff; font-size:.85rem; margin-top:4px; }

/* Search input */
[data-testid="stTextInput"] input {
    background:#08081e !important; border:1px solid #FFE81F44 !important;
    color:#e0e0f0 !important; border-radius:8px !important;
    font-family:'Exo 2',sans-serif !important;
}
[data-testid="stTextInput"] input:focus {
    border-color:#FFE81F !important;
    box-shadow:0 0 10px #FFE81F33 !important;
}

/* Scrollbar */
::-webkit-scrollbar { width:5px; }
::-webkit-scrollbar-track { background:#04040f; }
::-webkit-scrollbar-thumb {
    background:linear-gradient(180deg,#FFE81F,#aa9900); border-radius:3px;
}

/* Plotly charts */
.js-plotly-plot { border-radius:10px; overflow:hidden; }
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
st.sidebar.title("Navigation")
section = st.sidebar.radio("Go to", [
    "1. Abstract", "2. Dataset Description", "3. Descriptive Statistics",
    "4. Data Cleanup", "5. Plots", "6. Detailed Overview",
    "7. Data Transformation", "8. Hypothesis Check", "9. Discussion",
])

# ── Hero banner with animated counters ───────────────────────────────────────
st.markdown("""
<div style="
    background:linear-gradient(135deg,#04040f 0%,#0a0a25 50%,#04040f 100%);
    border:1px solid #FFE81F44; border-radius:14px;
    padding:36px 40px 30px; margin-bottom:28px;
    box-shadow:0 0 50px #FFE81F11, inset 0 0 80px #0000ff06;
    text-align:center;
">
    <div style="
        font-family:'Orbitron',sans-serif; font-size:2.5rem; font-weight:900;
        color:#FFE81F; text-shadow:0 0 30px #FFE81Faa,0 0 60px #FFE81F44;
        letter-spacing:.12em; margin-bottom:8px;
        animation:pulseGlow 4s ease-in-out infinite;
    ">STAR WARS UNIVERSE</div>
    <div style="
        font-family:'Orbitron',sans-serif; font-size:.8rem; color:#8888aa;
        letter-spacing:.25em; text-transform:uppercase; margin-bottom:28px;
    ">Exploratory Data Analysis &nbsp;·&nbsp; DSBA &nbsp;·&nbsp; HSE</div>
    <div style="display:flex;justify-content:center;gap:32px;flex-wrap:wrap;">
        <div style="text-align:center;">
            <div style="font-family:'Orbitron',sans-serif;font-size:1.8rem;color:#FFE81F;
                 text-shadow:0 0 15px #FFE81F88;animation:countUp .8s ease .1s both;">112</div>
            <div style="font-size:.72rem;color:#8888aa;letter-spacing:.12em;margin-top:2px;">CHARACTERS</div>
        </div>
        <div style="text-align:center;">
            <div style="font-family:'Orbitron',sans-serif;font-size:1.8rem;color:#4fc3f7;
                 text-shadow:0 0 15px #4fc3f788;animation:countUp .8s ease .2s both;">56</div>
            <div style="font-size:.72rem;color:#8888aa;letter-spacing:.12em;margin-top:2px;">STARSHIPS</div>
        </div>
        <div style="text-align:center;">
            <div style="font-family:'Orbitron',sans-serif;font-size:1.8rem;color:#ef5350;
                 text-shadow:0 0 15px #ef535088;animation:countUp .8s ease .3s both;">57</div>
            <div style="font-size:.72rem;color:#8888aa;letter-spacing:.12em;margin-top:2px;">WEAPONS</div>
        </div>
        <div style="text-align:center;">
            <div style="font-family:'Orbitron',sans-serif;font-size:1.8rem;color:#66bb6a;
                 text-shadow:0 0 15px #66bb6a88;animation:countUp .8s ease .4s both;">26</div>
            <div style="font-size:.72rem;color:#8888aa;letter-spacing:.12em;margin-top:2px;">PLANETS</div>
        </div>
        <div style="text-align:center;">
            <div style="font-family:'Orbitron',sans-serif;font-size:1.8rem;color:#ab47bc;
                 text-shadow:0 0 15px #ab47bc88;animation:countUp .8s ease .5s both;">39</div>
            <div style="font-size:.72rem;color:#8888aa;letter-spacing:.12em;margin-top:2px;">SPECIES</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── 1. Abstract ───────────────────────────────────────────────────────────────
if section == "1. Abstract":
    st.header("1. Abstract")

    st.markdown("""
<div style="overflow:hidden;height:300px;
    background:radial-gradient(ellipse at center bottom,#0a0a2a 0%,#000008 70%);
    border:1px solid #FFE81F33;border-radius:12px;margin-bottom:8px;position:relative;">
    <div style="position:absolute;width:80%;left:10%;
        animation:crawl 35s linear 1 forwards;text-align:center;padding-top:20px;">
        <p style="font-family:'Orbitron',sans-serif;font-size:.7rem;letter-spacing:.35em;color:#FFE81F66;margin-bottom:24px;">
            A LONG TIME AGO IN A GALAXY FAR, FAR AWAY...
        </p>
        <p style="font-size:1.05rem;line-height:2;color:#FFE81Fdd;margin-bottom:16px;">
            This project presents an exploratory data analysis of the
            <strong style="color:#FFE81F;">Star Wars universe</strong> dataset,
            containing information about characters, starships, planets, species, and weapons.
        </p>
        <p style="font-size:1rem;line-height:2;color:#FFE81Fcc;margin-bottom:16px;">
            The goal is to find patterns in physical characteristics of characters,
            technical parameters of starships, and relationships between variables.
        </p>
        <p style="font-size:.95rem;line-height:2;color:#FFE81Faa;margin-bottom:16px;">
            The dataset is composite — multiple interconnected CSV tables obtained from Kaggle.
        </p>
        <p style="font-family:'Orbitron',sans-serif;font-size:1.1rem;color:#FFE81F;
              text-shadow:0 0 20px #FFE81Faa;letter-spacing:.08em;">
            Tiniakov Rodion &amp; Belousov Zakhar
        </p>
    </div>
</div>
<p style="text-align:center;font-size:.72rem;color:#FFE81F44;
   font-family:'Orbitron',sans-serif;letter-spacing:.12em;margin-bottom:16px;">
    ↓ &nbsp; scroll below to read
</p>
""", unsafe_allow_html=True)

    st.markdown("""
<div style="overflow-y:auto;max-height:280px;
    background:linear-gradient(135deg,#08081a,#0d0d22);
    border:1px solid #FFE81F33;border-radius:12px;
    padding:28px 10%;text-align:center;
    box-shadow:0 0 20px #FFE81F0a;
    scrollbar-width:thin;scrollbar-color:#FFE81F55 #04040f;">
    <p style="font-family:'Orbitron',sans-serif;font-size:.7rem;letter-spacing:.35em;color:#FFE81F66;margin-bottom:24px;">
        A LONG TIME AGO IN A GALAXY FAR, FAR AWAY...
    </p>
    <p style="font-size:1.05rem;line-height:2;color:#FFE81Fdd;margin-bottom:16px;">
        This project presents an exploratory data analysis of the
        <strong style="color:#FFE81F;">Star Wars universe</strong> dataset,
        containing information about characters, starships, planets, species, and weapons.
    </p>
    <p style="font-size:1rem;line-height:2;color:#FFE81Fcc;margin-bottom:16px;">
        The goal is to find patterns in physical characteristics of characters,
        technical parameters of starships, and relationships between variables across tables.
    </p>
    <p style="font-size:.95rem;line-height:2;color:#FFE81Faa;margin-bottom:16px;">
        The dataset is composite — multiple interconnected CSV tables obtained from Kaggle.
        All stages of the analysis were performed by:
    </p>
    <p style="font-family:'Orbitron',sans-serif;font-size:1.15rem;color:#FFE81F;
          text-shadow:0 0 20px #FFE81Faa;letter-spacing:.08em;margin-top:8px;">
        Tiniakov Rodion &amp; Belousov Zakhar
    </p>
</div>
""", unsafe_allow_html=True)

# ── 2. Dataset Description ────────────────────────────────────────────────────
elif section == "2. Dataset Description":
    st.header("2. Dataset Description")

    # Search box
    search = st.text_input("🔍  Search characters by name or species", placeholder="e.g. Luke, Human, Wookiee...")
    if search:
        results = characters[
            characters["name"].str.contains(search, case=False, na=False) |
            characters["species"].str.contains(search, case=False, na=False)
        ]
        st.write(f"Found **{len(results)}** results:")
        for _, row in results.iterrows():
            h = f"{row['height']:.2f} m" if pd.notna(row.get("height")) else "—"
            w = f"{row['weight']:.0f} kg" if pd.notna(row.get("weight")) else "—"
            sp = row.get("species","—") if pd.notna(row.get("species")) else "—"
            gn = row.get("gender","—")  if pd.notna(row.get("gender"))  else "—"
            hw = row.get("homeworld","—") if pd.notna(row.get("homeworld")) else "—"
            st.markdown(f"""
<div class="char-card">
    <div class="char-name">{row['name']}</div>
    <div class="char-meta">{sp} &nbsp;·&nbsp; {gn} &nbsp;·&nbsp; {hw}</div>
    <div class="char-stat">Height: {h} &nbsp;|&nbsp; Weight: {w}</div>
</div>""", unsafe_allow_html=True)
        st.divider()

    st.write("""
    The dataset covers the Star Wars fictional universe and consists of **5 main tables**:
    - **characters.csv** — 112 rows, physical and biographical data
    - **planets.csv** — 26 rows, astronomical and geographical data
    - **starships.csv** — 56 rows, technical specifications
    - **species.csv** — 39 rows, biological characteristics
    - **weapons.csv** — 57 rows, specifications
    """)

    for name, df in [("characters", characters), ("planets", planets),
                     ("starships", starships), ("species", species), ("weapons", weapons)]:
        with st.expander(f"TABLE: {name.upper()} — {df.shape[0]} rows × {df.shape[1]} columns"):
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Data types:**")
                st.dataframe(df.dtypes.rename("dtype").to_frame())
            with col2:
                missing = df.isnull().sum()
                missing = missing[missing > 0]
                st.write("**Missing values:**")
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
        st.subheader(f"Table: {table.upper()}")
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
                           color_discrete_sequence=["#4fc3f7"])
        fig.update_traces(marker_line_color="#0d0d20", marker_line_width=1)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.histogram(starships_clean, x="length", nbins=15,
                           title="Distribution of Starship Length",
                           labels={"length":"Length (m)"}, template=PLOTLY_TEMPLATE,
                           color_discrete_sequence=["#ef5350"])
        fig.update_traces(marker_line_color="#0d0d20", marker_line_width=1)
        st.plotly_chart(fig, use_container_width=True)
    st.write("Height is roughly bell-shaped (~1.80 m). Starship length is heavily right-skewed — most ships under 100 m, with the Executor (19,000 m) as extreme outlier.")

    st.subheader("Scatter: Height vs Weight")
    fig = px.scatter(characters_clean, x="height", y="weight", hover_name="name",
                     color="species", title="Character Height vs Weight",
                     labels={"height":"Height (m)","weight":"Weight (kg)"},
                     template=PLOTLY_TEMPLATE)
    fig.update_traces(marker=dict(size=9, line=dict(width=1, color="#0d0d20")))
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
                 color_continuous_scale=["#0d0d20","#4fc3f7","#FFE81F"])
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
                 color_discrete_map={"Male":"#4fc3f7","Female":"#ef5350","unknown":"#ab47bc"})
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
                 color_continuous_scale=["#0d0d20","#ef5350","#FFE81F"])
    st.plotly_chart(fig, use_container_width=True)
    st.write("Weight mirrors height trends. High overall std (~149 kg) driven by extreme outliers.")

    st.subheader("Starship Length vs Crew Size by Class")
    fig = px.scatter(starships_clean, x="length", y="crew", color="starship_class",
                     hover_name="name", title="Starship Length vs Crew Size",
                     labels={"length":"Length (m)","crew":"Crew Size"},
                     template=PLOTLY_TEMPLATE)
    fig.update_traces(marker=dict(size=10, line=dict(width=1, color="#0d0d20")))
    st.plotly_chart(fig, use_container_width=True)
    st.write("Larger ships require more crew. The Executor (19,000 m, ~279,000 crew) is an extreme outlier.")

    st.subheader("Planet Diameter and Population")
    col1, col2 = st.columns(2)
    with col1:
        pdf = planets_clean.sort_values("diameter")
        fig = px.bar(pdf, x=pdf.index.astype(str), y="diameter", hover_name="name",
                     title="Planet Diameter", labels={"diameter":"Diameter (km)"},
                     template=PLOTLY_TEMPLATE, color_discrete_sequence=["#4fc3f7"])
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        pdf2 = planets_clean.sort_values("population")
        fig = px.bar(pdf2, x=pdf2.index.astype(str), y="population", hover_name="name",
                     title="Planet Population", labels={"population":"Population"},
                     template=PLOTLY_TEMPLATE, color_discrete_sequence=["#ef5350"])
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
                     template=PLOTLY_TEMPLATE, color_discrete_sequence=["#4fc3f7"])
        fig.update_layout(xaxis_tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        wca = (weapons_clean.dropna(subset=["cost_in_credits"])
               .groupby("type")["cost_in_credits"].mean().sort_values().reset_index())
        fig = px.bar(wca, x="type", y="cost_in_credits", title="Avg Cost by Type",
                     template=PLOTLY_TEMPLATE, color_discrete_sequence=["#ef5350"])
        fig.update_layout(xaxis_tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    with col3:
        wla = (weapons_clean.dropna(subset=["length"])
               .groupby("type")["length"].mean().sort_values().reset_index())
        fig = px.bar(wla, x="type", y="length", title="Avg Length by Type",
                     template=PLOTLY_TEMPLATE, color_discrete_sequence=["#ab47bc"])
        fig.update_layout(xaxis_tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    st.write("Blasters are most common. Missile weapons most expensive. Lightsabers notably compact.")

# ── 7. Data Transformation ────────────────────────────────────────────────────
elif section == "7. Data Transformation":
    st.header("7. Data Transformation")

    st.subheader("BMI for Characters")
    st.write("BMI = weight / height² — allows comparing body composition across species.")

    # Character cards for BMI top/bottom
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Highest BMI:**")
        for _, row in characters_clean.nlargest(5,"bmi").iterrows():
            st.markdown(f"""
<div class="char-card">
    <div class="char-name">{row['name']}</div>
    <div class="char-meta">{row.get('species','—')}</div>
    <div class="char-stat">BMI: <strong style="color:#ef5350;">{row['bmi']:.1f}</strong>
     &nbsp;|&nbsp; {row['height']:.2f} m &nbsp;/&nbsp; {row['weight']:.0f} kg</div>
</div>""", unsafe_allow_html=True)
    with col2:
        st.write("**Lowest BMI:**")
        for _, row in characters_clean.nsmallest(5,"bmi").iterrows():
            st.markdown(f"""
<div class="char-card">
    <div class="char-name">{row['name']}</div>
    <div class="char-meta">{row.get('species','—')}</div>
    <div class="char-stat">BMI: <strong style="color:#66bb6a;">{row['bmi']:.1f}</strong>
     &nbsp;|&nbsp; {row['height']:.2f} m &nbsp;/&nbsp; {row['weight']:.0f} kg</div>
</div>""", unsafe_allow_html=True)

    st.write("**Full table (first 10 rows):**")
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
        template=PLOTLY_TEMPLATE, color_discrete_sequence=["#FFE81F"]
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
    fig.update_traces(marker=dict(size=10, line=dict(width=1, color="#0d0d20")))
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
                 color_discrete_map={"Human":"#4fc3f7","Non-Human":"#ef5350"})
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
