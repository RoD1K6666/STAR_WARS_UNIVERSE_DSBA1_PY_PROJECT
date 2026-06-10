import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import streamlit as st
from scipy.stats import pearsonr

st.set_page_config(page_title="Star Wars — a data study", layout="wide", page_icon="✦")

# Palette: warm near-black ground, three accents (sand / oxblood / sky)
GROUND  = "#17130d"
PANEL   = "#1f1a12"
SAND    = "#d8b878"
OXBLOOD = "#9e3b32"
SKY     = "#6f9bc4"
AMBER   = "#c98b3a"
SAGE    = "#7a9b6f"
MAUVE   = "#b06b8a"
INK     = "#e3dac8"
MUTED   = "#9a8f78"

# ── Plotly template ───────────────────────────────────────────────────────────
PLOTLY_TEMPLATE = dict(
    layout=go.Layout(
        paper_bgcolor=PANEL,
        plot_bgcolor=PANEL,
        font=dict(color="#cabda4", family="Spectral, serif", size=13),
        title=dict(font=dict(family="Fraunces, serif", size=18, color=INK)),
        xaxis=dict(gridcolor="rgba(216,184,120,0.08)", linecolor="rgba(216,184,120,0.25)", zeroline=False),
        yaxis=dict(gridcolor="rgba(216,184,120,0.08)", linecolor="rgba(216,184,120,0.25)", zeroline=False),
        colorway=[SAND, SKY, OXBLOOD, AMBER, SAGE, MAUVE],
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
)

# ── Matplotlib ────────────────────────────────────────────────────────────────
plt.style.use("dark_background")
plt.rcParams.update({
    "figure.facecolor": PANEL, "axes.facecolor": PANEL,
    "axes.edgecolor": "#4a3f2c", "axes.labelcolor": "#cabda4",
    "xtick.color": "#cabda4", "ytick.color": "#cabda4",
    "text.color": "#cabda4", "grid.color": "#2a2317", "grid.alpha": 0.6,
})

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,500;0,9..144,600;1,9..144,400&family=Spectral:ital,wght@0,300;0,400;0,500;0,600;1,400&display=swap');

:root {{
    --ground:{GROUND}; --panel:{PANEL};
    --sand:{SAND}; --oxblood:{OXBLOOD}; --sky:{SKY};
    --ink:{INK}; --muted:{MUTED}; --line:rgba(216,184,120,0.14);
}}

html, body, [class*="css"] {{ font-family:'Spectral', Georgia, serif; }}

.stApp {{ background:var(--ground); }}

/* asymmetric measure — not dead-centred */
.block-container {{ max-width:980px; padding-top:2rem; padding-left:3.2rem; padding-right:2rem; }}

/* Sidebar */
[data-testid="stSidebar"] {{ background:#13100b; border-right:1px solid var(--line); }}
[data-testid="stSidebar"] .side-title {{
    font-family:'Fraunces',serif; font-weight:500; font-size:1.5rem;
    color:var(--ink); line-height:1.05; margin:.2rem 0 .1rem;
}}
[data-testid="stSidebar"] .side-sub {{
    font-family:'Spectral',serif; font-style:italic; color:var(--oxblood);
    font-size:.92rem; margin-bottom:1.3rem;
}}
[data-testid="stSidebar"] label {{ color:#c4b89c !important; font-size:.96rem !important; }}

/* Headings — Fraunces, normal case, short oxblood tick above */
h1, h2, h3 {{ text-transform:none !important; letter-spacing:normal !important; }}
h2 {{
    font-family:'Fraunces',serif !important; font-weight:500 !important;
    color:var(--ink) !important; font-size:2rem !important;
    margin-top:2.4rem !important; margin-bottom:.4rem !important; line-height:1.1;
}}
h2::before {{
    content:""; display:block; width:36px; height:3px;
    background:var(--oxblood); margin-bottom:.6rem;
}}
h3 {{
    font-family:'Spectral',serif !important; font-style:italic; font-weight:400 !important;
    color:#b6aa90 !important; font-size:1.28rem !important; margin-top:1.5rem !important;
}}

p, li {{ color:#cdc2a8; line-height:1.72; font-size:1rem; }}
strong {{ color:var(--sand) !important; font-weight:600; }}

/* Metrics — stripped of tile chrome, read as a stat line */
[data-testid="metric-container"] {{ background:transparent; border:none; padding:6px 0; }}
[data-testid="metric-container"] label {{
    color:var(--muted) !important; font-family:'Spectral',serif !important;
    font-style:italic; font-size:.92rem !important; letter-spacing:normal;
    text-transform:none;
}}
[data-testid="metric-container"] [data-testid="stMetricValue"] {{
    color:var(--ink) !important; font-family:'Fraunces',serif !important;
    font-weight:600; font-size:2rem !important;
}}

/* Dataframe / expander */
[data-testid="stDataFrame"] {{ border:1px solid var(--line) !important; border-radius:3px; }}
[data-testid="stExpander"] {{ border:1px solid var(--line) !important; border-radius:3px; background:var(--panel); }}
details summary {{
    font-family:'Fraunces',serif !important; color:var(--ink) !important;
    font-size:1rem !important; font-weight:500;
}}

/* Divider — short, left-set, not a full-width hairline */
hr {{
    border:none !important; border-top:1px solid var(--line) !important;
    width:120px !important; margin:2.2rem 0 !important;
}}

/* Text input */
[data-testid="stTextInput"] input {{
    background:var(--panel) !important; border:1px solid var(--line) !important;
    color:var(--ink) !important; border-radius:3px !important; font-family:'Spectral',serif !important;
}}
[data-testid="stTextInput"] input:focus {{ border-color:var(--sand) !important; box-shadow:none !important; }}

/* Lead / hero — editorial, offset, numbers live in prose */
.lead {{ margin:.5rem 0 2.6rem; }}
.lead .eyebrow {{ font-family:'Spectral',serif; font-style:italic; color:var(--oxblood); font-size:1rem; margin-bottom:.6rem; }}
.lead .title {{
    font-family:'Fraunces',serif; font-weight:500; font-size:3.3rem;
    line-height:1.0; color:var(--ink); margin:0;
}}
.lead .title .ind {{ display:block; padding-left:1.7em; color:var(--sand); }}
.lead .text {{
    font-family:'Spectral',serif; font-size:1.18rem; line-height:1.7;
    color:#d3c8ad; max-width:56ch; margin:1.4rem 0 0;
}}
.lead .text b {{ color:var(--sand); font-weight:600; }}
.lead .by {{ font-family:'Spectral',serif; font-style:italic; color:var(--muted); margin-top:1.1rem; padding-left:1.7em; }}

/* Record card */
.sw-card {{
    background:var(--panel); border:1px solid var(--line);
    border-left:2px solid var(--oxblood); border-radius:2px;
    padding:11px 16px; margin-bottom:7px;
}}
.sw-card .name {{ font-family:'Fraunces',serif; font-weight:500; color:var(--ink); font-size:1.12rem; }}
.sw-card .meta {{ font-family:'Spectral',serif; font-style:italic; color:var(--muted); font-size:.9rem; margin-top:1px; }}
.sw-card .stat {{ color:#c0b599; font-size:.9rem; margin-top:5px; }}

/* Scrollbar */
::-webkit-scrollbar {{ width:9px; }}
::-webkit-scrollbar-track {{ background:transparent; }}
::-webkit-scrollbar-thumb {{ background:#3a3120; border-radius:5px; }}
::-webkit-scrollbar-thumb:hover {{ background:#4d4129; }}
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
    '<div class="side-title">Star Wars</div>'
    '<div class="side-sub">a data study</div>',
    unsafe_allow_html=True)
section = st.sidebar.radio("Section", [
    "1. Abstract", "2. Dataset Description", "3. Descriptive Statistics",
    "4. Data Cleanup", "5. Plots", "6. Detailed Overview",
    "7. Data Transformation", "8. Hypothesis Check", "9. Discussion",
], label_visibility="collapsed")

# ── Lead ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="lead">
    <div class="eyebrow">Star Wars, by the numbers</div>
    <div class="title">The shape<span class="ind">of a galaxy</span></div>
    <div class="text">
        Before us: <b>{characters.shape[0]}</b> characters, <b>{starships.shape[0]}</b> starships,
        <b>{planets.shape[0]}</b> worlds, <b>{species.shape[0]}</b> species and
        <b>{weapons.shape[0]}</b> weapons — five tables drawn from a single Kaggle dataset,
        and somewhere between them, a pattern worth finding.
    </div>
    <div class="by">Tiniakov Rodion &amp; Belousov Zakhar</div>
</div>
""", unsafe_allow_html=True)

# ── 1. Abstract ───────────────────────────────────────────────────────────────
if section == "1. Abstract":
    st.header("1. Abstract")
    st.write("""
This project is an exploratory data analysis of the Star Wars universe — a composite dataset
of five interconnected CSV tables describing its characters, starships, planets, species, and
weapons. Part of the work is simply reconciling those tables into a clean analytical base; the
rest is looking for structure inside it.

We move through descriptive statistics, data cleanup, visualisation, and a pair of engineered
features, then put two concrete claims to a formal test: that larger starships fly slower, and
that humans vary less in build than the galaxy's stranger species. The closing discussion weighs
what held up, what didn't, and where the data quietly lies.
""")
    st.markdown('<hr>', unsafe_allow_html=True)
    st.markdown(
        '<p style="font-family:Spectral,serif;font-style:italic;color:#9a8f78;">'
        'Tiniakov Rodion &amp; Belousov Zakhar — DSBA, HSE.</p>',
        unsafe_allow_html=True)

# ── 2. Dataset Description ────────────────────────────────────────────────────
elif section == "2. Dataset Description":
    st.header("2. Dataset Description")

    search = st.text_input("Search a character by name or species", placeholder="Luke, Wookiee, Human…")
    if search:
        results = characters[
            characters["name"].str.contains(search, case=False, na=False) |
            characters["species"].str.contains(search, case=False, na=False)
        ]
        st.write(f"*{len(results)} on file.*")
        for _, row in results.iterrows():
            h = f"{row['height']:.2f} m" if pd.notna(row.get("height")) else "—"
            w = f"{row['weight']:.0f} kg" if pd.notna(row.get("weight")) else "—"
            sp = row.get("species","—") if pd.notna(row.get("species")) else "—"
            gn = row.get("gender","—")  if pd.notna(row.get("gender"))  else "—"
            hw = row.get("homeworld","—") if pd.notna(row.get("homeworld")) else "—"
            st.markdown(f"""
<div class="sw-card">
    <div class="name">{row['name']}</div>
    <div class="meta">{sp} · {gn} · {hw}</div>
    <div class="stat">{h} tall, {w}</div>
</div>""", unsafe_allow_html=True)
        st.markdown('<hr>', unsafe_allow_html=True)

    st.write("""
The dataset covers the Star Wars fictional universe across five tables — **characters**
(physical and biographical), **planets** (astronomical and geographical), **starships**
(technical specs), **species** (biology), and **weapons** (specs). Each is summarised below.
""")

    for name, df in [("characters", characters), ("planets", planets),
                     ("starships", starships), ("species", species), ("weapons", weapons)]:
        with st.expander(f"{name} — {df.shape[0]} rows, {df.shape[1]} columns"):
            col1, col2 = st.columns([3, 2])
            with col1:
                st.write("*Data types*")
                st.dataframe(df.dtypes.rename("dtype").to_frame())
            with col2:
                missing = df.isnull().sum()
                missing = missing[missing > 0]
                st.write("*Missing values*")
                if missing.empty:
                    st.success("None.")
                else:
                    st.dataframe(missing.rename("missing").to_frame())

# ── 3. Descriptive Statistics ─────────────────────────────────────────────────
elif section == "3. Descriptive Statistics":
    st.header("3. Descriptive Statistics")
    st.write("Centre and spread for the fields that carry the analysis.")

    fields = {
        "characters": ["height","weight"],
        "planets":    ["diameter","population","orbital_period"],
        "starships":  ["length","crew","MGLT"],
        "species":    ["average_height","average_lifespan"],
    }
    dfs = {"characters":characters,"planets":planets,"starships":starships,"species":species}

    for table, cols in fields.items():
        st.subheader(table)
        rows = []
        for col in cols:
            s = dfs[table][col].dropna()
            rows.append({"field":col,"mean":round(s.mean(),2),"median":round(s.median(),2),
                         "std":round(s.std(),2),"min":round(s.min(),2),"max":round(s.max(),2)})
        st.dataframe(pd.DataFrame(rows).set_index("field"))

# ── 4. Data Cleanup ───────────────────────────────────────────────────────────
elif section == "4. Data Cleanup":
    st.header("4. Data Cleanup")
    st.write("""
Rather than impute, rows missing the key numerical columns were dropped — a blunt choice, but
honest about what the data does and doesn't hold. The cost was uneven across tables.
""")

    cleanup = pd.DataFrame({
        "table":   ["characters", "starships", "planets"],
        "before":  [characters.shape[0], starships.shape[0], planets.shape[0]],
        "after":   [characters_clean.shape[0], starships_clean.shape[0], planets_clean.shape[0]],
    })
    cleanup["removed"] = cleanup["before"] - cleanup["after"]
    cleanup["kept %"]  = (100 * cleanup["after"] / cleanup["before"]).round(0).astype(int)
    st.dataframe(cleanup.set_index("table"))

    st.write(f"""
Characters lost **{characters.shape[0] - characters_clean.shape[0]}** of
{characters.shape[0]} rows; planets fell to **{planets_clean.shape[0]}**. The survivors keep
clean numeric types throughout.
""")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("characters")
        st.dataframe(characters_clean.dtypes.rename("dtype").to_frame())
    with col2:
        st.subheader("starships")
        st.dataframe(starships_clean.dtypes.rename("dtype").to_frame())

# ── 5. Plots ──────────────────────────────────────────────────────────────────
elif section == "5. Plots":
    st.header("5. Plots for Numerical Fields")

    st.subheader("two distributions")
    col1, col2 = st.columns([1, 1])
    with col1:
        fig = px.histogram(characters_clean, x="height", nbins=15,
                           title="Character height",
                           labels={"height":"Height (m)"}, template=PLOTLY_TEMPLATE,
                           color_discrete_sequence=[SKY])
        fig.update_traces(marker_line_color=PANEL, marker_line_width=1)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.histogram(starships_clean, x="length", nbins=15,
                           title="Starship length",
                           labels={"length":"Length (m)"}, template=PLOTLY_TEMPLATE,
                           color_discrete_sequence=[OXBLOOD])
        fig.update_traces(marker_line_color=PANEL, marker_line_width=1)
        st.plotly_chart(fig, use_container_width=True)
    st.write("Height is roughly bell-shaped around 1.80 m. Starship length is heavily right-skewed — most ships under 100 m, with the Executor (19,000 m) as an extreme outlier.")

    st.subheader("height against weight")
    fig = px.scatter(characters_clean, x="height", y="weight", hover_name="name",
                     color="species", title="Height vs weight, by species",
                     labels={"height":"Height (m)","weight":"Weight (kg)"},
                     template=PLOTLY_TEMPLATE)
    fig.update_traces(marker=dict(size=9, line=dict(width=1, color=PANEL)))
    st.plotly_chart(fig, use_container_width=True)
    st.write("A clear positive relationship, with a handful of bodies that refuse it. Hover any point for the name.")

    st.subheader("who stands tallest")
    top_sp = characters_clean["species"].value_counts().head(6).index
    avg_h  = (characters_clean[characters_clean["species"].isin(top_sp)]
              .groupby("species")["height"].mean().sort_values().reset_index())
    fig = px.bar(avg_h, x="species", y="height",
                 title="Average height by species (top 6)",
                 labels={"height":"Avg height (m)","species":"Species"},
                 template=PLOTLY_TEMPLATE, color="height",
                 color_continuous_scale=[PANEL, SKY, SAND])
    st.plotly_chart(fig, use_container_width=True)
    st.write("Wookiees top the chart near 2.28 m; humans sit close to the overall mean of ~1.78 m.")

# ── 6. Detailed Overview ──────────────────────────────────────────────────────
elif section == "6. Detailed Overview":
    st.header("6. Detailed Overview")

    st.subheader("height, split by gender")
    fig = px.box(characters_clean, x="gender", y="height", color="gender",
                 title="Height distribution by gender",
                 labels={"height":"Height (m)","gender":"Gender"},
                 template=PLOTLY_TEMPLATE,
                 color_discrete_map={"Male":SKY,"Female":OXBLOOD,"unknown":MAUVE})
    st.plotly_chart(fig, use_container_width=True)
    st.write("Male characters carry a higher median (~1.83 m vs ~1.70 m) and a wider spread.")

    st.subheader("weight by species")
    top5 = characters_clean["species"].value_counts().head(5).index
    avg_w = (characters_clean[characters_clean["species"].isin(top5)]
             .groupby("species")["weight"].mean().sort_values().reset_index())
    fig = px.bar(avg_w, x="species", y="weight",
                 title="Average weight by species (top 5)",
                 labels={"weight":"Avg weight (kg)","species":"Species"},
                 template=PLOTLY_TEMPLATE, color="weight",
                 color_continuous_scale=[PANEL, OXBLOOD, SAND])
    st.plotly_chart(fig, use_container_width=True)
    st.write("Weight tracks height, but a ~149 kg standard deviation betrays a few enormous outliers.")

    st.subheader("ships need crews")
    fig = px.scatter(starships_clean, x="length", y="crew", color="starship_class",
                     hover_name="name", title="Starship length vs crew size",
                     labels={"length":"Length (m)","crew":"Crew size"},
                     template=PLOTLY_TEMPLATE)
    fig.update_traces(marker=dict(size=10, line=dict(width=1, color=PANEL)))
    st.plotly_chart(fig, use_container_width=True)
    st.write("Bigger hulls demand bigger crews; the Executor (19,000 m, ~279,000 hands) sits in a class of its own.")

    st.subheader("worlds, by size and by people")
    col1, col2 = st.columns([1, 1])
    with col1:
        pdf = planets_clean.sort_values("diameter")
        fig = px.bar(pdf, x=pdf.index.astype(str), y="diameter", hover_name="name",
                     title="Planet diameter", labels={"diameter":"Diameter (km)"},
                     template=PLOTLY_TEMPLATE, color_discrete_sequence=[SKY])
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        pdf2 = planets_clean.sort_values("population")
        fig = px.bar(pdf2, x=pdf2.index.astype(str), y="population", hover_name="name",
                     title="Planet population", labels={"population":"Population"},
                     template=PLOTLY_TEMPLATE, color_discrete_sequence=[OXBLOOD])
        st.plotly_chart(fig, use_container_width=True)
    st.write("Diameters huddle between 10,000 and 13,000 km; populations sprawl across orders of magnitude, one world brushing a trillion.")

    st.subheader("what correlates with what")
    col1, col2 = st.columns([1, 1])
    chars_tmp = characters_clean.copy()
    chars_tmp["bmi"] = chars_tmp["weight"] / chars_tmp["height"]**2
    with col1:
        corr = chars_tmp[["height","weight","bmi"]].corr()
        fig = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r",
                        title="Characters", template=PLOTLY_TEMPLATE, zmin=-1, zmax=1)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        ship_cols = ["length","crew","MGLT","passengers","cargo_capacity","hyperdrive_rating"]
        corr2 = starships_clean[ship_cols].corr()
        fig = px.imshow(corr2, text_auto=".2f", color_continuous_scale="RdBu_r",
                        title="Starships", template=PLOTLY_TEMPLATE, zmin=-1, zmax=1)
        st.plotly_chart(fig, use_container_width=True)
    st.write("For bodies, height and weight move together while BMI pulls against height. For ships, size metrics cluster tightly, and MGLT speed leans faintly the other way.")

    st.subheader("an arsenal, counted")
    weapons_clean = weapons.dropna(subset=["type"])
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        wc = weapons_clean["type"].value_counts().reset_index()
        fig = px.bar(wc, x="type", y="count", title="Count by type",
                     template=PLOTLY_TEMPLATE, color_discrete_sequence=[SKY])
        fig.update_layout(xaxis_tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        wca = (weapons_clean.dropna(subset=["cost_in_credits"])
               .groupby("type")["cost_in_credits"].mean().sort_values().reset_index())
        fig = px.bar(wca, x="type", y="cost_in_credits", title="Avg cost",
                     template=PLOTLY_TEMPLATE, color_discrete_sequence=[OXBLOOD])
        fig.update_layout(xaxis_tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    with col3:
        wla = (weapons_clean.dropna(subset=["length"])
               .groupby("type")["length"].mean().sort_values().reset_index())
        fig = px.bar(wla, x="type", y="length", title="Avg length",
                     template=PLOTLY_TEMPLATE, color_discrete_sequence=[MAUVE])
        fig.update_layout(xaxis_tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    st.write("Blasters dominate by count, missiles by price, and the lightsaber — fittingly — stays the most compact of all.")

# ── 7. Data Transformation ────────────────────────────────────────────────────
elif section == "7. Data Transformation":
    st.header("7. Data Transformation")

    st.subheader("a body-mass index for aliens")
    st.write("BMI = weight ÷ height². A crude single number, but it lets a Hutt and a Jedi share an axis.")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.write("*Heaviest for their height*")
        for _, row in characters_clean.nlargest(5,"bmi").iterrows():
            st.markdown(f"""
<div class="sw-card">
    <div class="name">{row['name']}</div>
    <div class="meta">{row.get('species','—')}</div>
    <div class="stat">BMI <strong>{row['bmi']:.1f}</strong> · {row['height']:.2f} m / {row['weight']:.0f} kg</div>
</div>""", unsafe_allow_html=True)
    with col2:
        st.write("*Leanest*")
        for _, row in characters_clean.nsmallest(5,"bmi").iterrows():
            st.markdown(f"""
<div class="sw-card">
    <div class="name">{row['name']}</div>
    <div class="meta">{row.get('species','—')}</div>
    <div class="stat">BMI <strong>{row['bmi']:.1f}</strong> · {row['height']:.2f} m / {row['weight']:.0f} kg</div>
</div>""", unsafe_allow_html=True)

    st.write("*First ten rows*")
    st.dataframe(characters_clean[["name","species","height","weight","bmi"]].head(10).reset_index(drop=True))

    st.markdown('<hr>', unsafe_allow_html=True)
    st.subheader("passengers per metre")
    st.write("passengers ÷ length — a rough measure of how much a hull is built to carry rather than fight.")
    st.dataframe(starships_clean[["name","length","passengers","passengers_per_meter"]].head(10).reset_index(drop=True))
    fig = px.bar(
        starships_clean.dropna(subset=["passengers_per_meter"])
                       .sort_values("passengers_per_meter", ascending=False).head(15),
        x="name", y="passengers_per_meter",
        title="Fifteen most passenger-dense ships",
        labels={"passengers_per_meter":"Passengers / m","name":"Ship"},
        template=PLOTLY_TEMPLATE, color_discrete_sequence=[SAND]
    )
    fig.update_layout(xaxis_tickangle=45)
    st.plotly_chart(fig, use_container_width=True)

# ── 8. Hypothesis Check ───────────────────────────────────────────────────────
elif section == "8. Hypothesis Check":
    st.header("8. Hypothesis Check")

    st.subheader("first claim — bigger ships fly slower")
    st.write("If length and MGLT speed are at odds, we should see a negative correlation.")
    h1 = starships_clean[["name","length","MGLT","starship_class"]].dropna()
    fig = px.scatter(h1, x="length", y="MGLT", hover_name="name",
                     color="starship_class", trendline="ols",
                     title="Starship length vs MGLT speed",
                     labels={"length":"Length (m)","MGLT":"MGLT"},
                     template=PLOTLY_TEMPLATE)
    fig.update_traces(marker=dict(size=10, line=dict(width=1, color=PANEL)))
    st.plotly_chart(fig, use_container_width=True)
    corr, pval = pearsonr(h1["length"], h1["MGLT"])
    col1,col2,col3 = st.columns([1,1,1])
    col1.metric("Pearson r", f"{corr:.3f}")
    col2.metric("p-value",   f"{pval:.4f}")
    col3.metric("n", len(h1))
    st.write(f"r = {corr:.3f} at p = {pval:.3f} — real, but moderate. **Partially confirmed**: length pulls speed down without deciding it.")

    st.markdown('<hr>', unsafe_allow_html=True)

    st.subheader("second claim — humans are the uniform ones")
    st.write("If humans vary less in build, their BMI should spread far less than everyone else's.")
    humans     = characters_clean[characters_clean["species"]=="Human"]["bmi"].dropna()
    non_humans = characters_clean[characters_clean["species"]!="Human"]["bmi"].dropna()
    bmi_df = pd.concat([
        humans.rename("bmi").to_frame().assign(group="Human"),
        non_humans.rename("bmi").to_frame().assign(group="Non-Human")
    ])
    fig = px.box(bmi_df, x="group", y="bmi", color="group",
                 title="BMI — humans against everyone else",
                 labels={"bmi":"BMI","group":"Group"},
                 template=PLOTLY_TEMPLATE, points="all",
                 color_discrete_map={"Human":SKY,"Non-Human":OXBLOOD})
    st.plotly_chart(fig, use_container_width=True)
    stats = pd.DataFrame({
        "group":  ["Human","Non-Human"],
        "n":      [len(humans), len(non_humans)],
        "mean":   [round(humans.mean(),2), round(non_humans.mean(),2)],
        "std":    [round(humans.std(),2),  round(non_humans.std(),2)],
        "min":    [round(humans.min(),2),  round(non_humans.min(),2)],
        "max":    [round(humans.max(),2),  round(non_humans.max(),2)],
    }).set_index("group")
    st.dataframe(stats)
    st.write("Human BMI scatters by ~2.9; the rest of the galaxy by ~13.9 — nearly five times as wide. **Confirmed.**")

# ── 9. Discussion ─────────────────────────────────────────────────────────────
elif section == "9. Discussion":
    st.header("9. Discussion")

    for title, body in [
        ("the data, and what it cost",
         "Five interconnected tables, cleaned by deletion rather than guesswork. The price was uneven: characters shed roughly a third of their rows once missing height and weight were dropped, and planets fell from 26 to 11. What remains is trustworthy, but smaller than it looks."),
        ("centre and spread",
         "Character heights sit tightly around 1.80 m (std 0.38). Starship length is the opposite — a median of 20.75 m against a mean of 604, the gap entirely the work of a few giants. Crew follows suit (median 1, mean 7,344). Only MGLT speed behaves, spanning a tame 20–120."),
        ("what the pictures showed",
         "Height is near-normal; height and weight rise together with loud exceptions. Wookiees are tallest and heaviest, male characters taller on average and more variable, and larger ships reliably need larger crews. Planet population, alone, refuses any tidy scale."),
        ("two engineered numbers",
         "BMI lands in a believable 16–34 for humanoids and goes haywire for the likes of Jabba and Yoda — which is the point: it flags the bodies that break the mould. Passengers-per-metre cleanly separates warships (zero) from transports (one to two per metre)."),
        ("the verdicts",
         "Bigger ships do fly slower, but only somewhat — r = −0.384 at p = 0.010, significant yet far from deterministic. Humans really are the uniform ones: their BMI varies almost five times less than the rest of the galaxy's, a spread driven by species built to entirely different blueprints."),
    ]:
        st.subheader(title)
        st.write(body)
