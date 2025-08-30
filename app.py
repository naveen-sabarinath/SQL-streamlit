# app.py — SQL-first Streamlit dashboard (tables only, no graphs)
from urllib.parse import quote_plus
import datetime as dt
import pandas as pd
from sqlalchemy import create_engine, text
import streamlit as st

# ---------- CONFIG ----------
DB_USER  = "root"
DB_PASS  = "root"
DB_HOST  = "localhost"
DB_PORT  = 3306
DB_NAME  = "traffic_stops"
DB_TABLE = "police"

# Column names (edit to your schema)
DATE_COL        = "stop_date"
TIME_COL        = "stop_time"
COUNTRY_COL     = "country_name"
GENDER_COL      = "driver_gender"
RACE_COL        = "driver_race"
VIOLATION_COL   = "violation"
SEARCH_COL      = "search_conducted"
ARREST_COL      = "is_arrested"
DRUGS_COL       = "drugs_related_stop"
DURATION_COL    = ""
VEHICLE_COL     = "vehicle_number"
AGE_COL         = "driver_age"

# ---------- STREAMLIT PAGE ----------
st.set_page_config(page_title="SQL-Only Police Dashboard", page_icon="🧮", layout="wide")
st.title("🧮 Police Stops — Dashboard ")

# ---------- DB CONNECTION ----------
@st.cache_resource
def get_engine():
    url = f"mysql+pymysql://{DB_USER}:{quote_plus(DB_PASS)}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    return create_engine(url, pool_pre_ping=True)

@st.cache_data(show_spinner=False)
def run_query(sql: str, params: dict | None = None) -> pd.DataFrame:
    eng = get_engine()
    with eng.connect() as con:
        return pd.read_sql(text(sql), con, params=params)

# Helpers for options / IN-clauses ------------------------------------------------
@st.cache_data(show_spinner=False)
def distinct_values(col: str) -> list:
    if not col:
        return []
    df = run_query(f"SELECT DISTINCT {col} AS v FROM {DB_TABLE} WHERE {col} IS NOT NULL ORDER BY v")
    return [x for x in df["v"].tolist() if x is not None]

@st.cache_data(show_spinner=False)
def date_bounds(col: str):
    if not col:
        return None, None
    df = run_query(f"SELECT MIN({col}) AS mn, MAX({col}) AS mx FROM {DB_TABLE}")
    mn, mx = df.loc[0, "mn"], df.loc[0, "mx"]
    # Coerce to date
    if isinstance(mn, pd.Timestamp):
        mn = mn.date()
    if isinstance(mx, pd.Timestamp):
        mx = mx.date()
    return mn, mx


def make_in_clause(column: str, key_prefix: str, values: list[str], params: dict):
    """Return (clause_sql, updated_params). Uses named params :key_prefix0, :key_prefix1, ..."""
    if not values:
        return None
    keys = []
    for i, val in enumerate(values):
        k = f"{key_prefix}{i}"
        params[k] = val
        keys.append(f":{k}")
    clause = f"{column} IN (" + ",".join(keys) + ")"
    return clause

# ===================== SIDEBAR =====================
st.sidebar.title("Navigation")
section = st.sidebar.radio(
    "Go to",
    (
        "🚗 Vehicle-Based",
        "👥 Demographic",
        "⏱️ Time & Duration",
        "⚖️ Violation",
        "🗺️ Location",
        "🧠 Complex",
        "🗂️ Sample Records",
    ),
    index=0,
)

st.sidebar.markdown("---")
st.sidebar.subheader("Filters")
params: dict = {}
conditions: list[str] = ["1=1"]

# Date range filter
if DATE_COL:
    mn, mx = date_bounds(DATE_COL)
    if mn and mx:
        dflt = (mn, mx)
        date_range = st.sidebar.date_input("Date range", value=dflt, min_value=mn, max_value=mx)
        # date_input returns a single date when user picks one; normalize to tuple
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start, end = date_range
        else:
            start, end = dflt[0], dflt[1]
        conditions.append(f"{DATE_COL} BETWEEN :date_start AND :date_end")
        params["date_start"] = dt.datetime.combine(start, dt.time.min)
        params["date_end"]   = dt.datetime.combine(end, dt.time.max)

# Country filter
if COUNTRY_COL:
    countries = distinct_values(COUNTRY_COL)
    if countries:
        sel_c = st.sidebar.multiselect("Country", countries)
        if sel_c:
            c_clause = make_in_clause(COUNTRY_COL, "c_", sel_c, params)
            conditions.append(c_clause)

# Gender filter
if GENDER_COL:
    genders = distinct_values(GENDER_COL)
    if genders:
        sel_g = st.sidebar.multiselect("Gender", genders)
        if sel_g:
            g_clause = make_in_clause(GENDER_COL, "g_", sel_g, params)
            conditions.append(g_clause)

# Race filter
if RACE_COL:
    races = distinct_values(RACE_COL)
    if races:
        sel_r = st.sidebar.multiselect("Race", races)
        if sel_r:
            r_clause = make_in_clause(RACE_COL, "r_", sel_r, params)
            conditions.append(r_clause)

# Violation filter
if VIOLATION_COL:
    violations = distinct_values(VIOLATION_COL)
    if violations:
        sel_v = st.sidebar.multiselect("Violation", violations)
        if sel_v:
            v_clause = make_in_clause(VIOLATION_COL, "v_", sel_v, params)
            conditions.append(v_clause)

# Boolean toggles
if SEARCH_COL:
    only_search = st.sidebar.checkbox("Only where search conducted", value=False)
    if only_search:
        conditions.append(f"{SEARCH_COL} = 1")

if ARREST_COL:
    only_arrest = st.sidebar.checkbox("Only arrests", value=False)
    if only_arrest:
        conditions.append(f"{ARREST_COL} = 1")

if DRUGS_COL:
    only_drugs = st.sidebar.checkbox("Only drug-related stops", value=False)
    if only_drugs:
        conditions.append(f"{DRUGS_COL} = 1")

WHERE_SQL = " AND ".join([c for c in conditions if c])

# ===================== KPIs =====================
c1, c2, c3, c4 = st.columns(4)

# Total stops
kpi_df = run_query(f"SELECT COUNT(*) AS total FROM {DB_TABLE} WHERE {WHERE_SQL}", params)
with c1:
    st.metric("Total Stops", f"{int(kpi_df.loc[0, 'total']):,}")

# Arrest rate
if ARREST_COL:
    a = run_query(f"SELECT AVG({ARREST_COL}=1) AS rate FROM {DB_TABLE} WHERE {WHERE_SQL}", params).loc[0, "rate"]
    with c2:
        st.metric("Arrest Rate", f"{(a or 0)*100:.1f}%")

# Search rate
if SEARCH_COL:
    s = run_query(f"SELECT AVG({SEARCH_COL}=1) AS rate FROM {DB_TABLE} WHERE {WHERE_SQL}", params).loc[0, "rate"]
    with c3:
        st.metric("Search Rate", f"{(s or 0)*100:.1f}%")

# Drug-related rate
if DRUGS_COL:
    dr = run_query(f"SELECT AVG({DRUGS_COL}=1) AS rate FROM {DB_TABLE} WHERE {WHERE_SQL}", params).loc[0, "rate"]
    with c4:
        st.metric("Drug Stops", f"{(dr or 0)*100:.1f}%")

st.divider()

# ===================== SECTIONS =====================

def show_vehicle():
    st.subheader("Top 10 vehicles in drug-related stops")
    if not VEHICLE_COL or not DRUGS_COL:
        st.info("Vehicle or drug-related column not configured.")
        return
    q1 = f"""
        SELECT {VEHICLE_COL} AS vehicle_number, COUNT(*) AS drug_stops
        FROM {DB_TABLE}
        WHERE {WHERE_SQL} AND {DRUGS_COL}=1 AND {VEHICLE_COL} IS NOT NULL
        GROUP BY {VEHICLE_COL}
        ORDER BY drug_stops DESC
        LIMIT 10
    """
    st.dataframe(run_query(q1, params))

    st.subheader("Most frequently searched vehicles")
    if not SEARCH_COL:
        st.info("Search column not configured.")
        return
    q2 = f"""
        SELECT {VEHICLE_COL} AS vehicle_number, COUNT(*) AS searches
        FROM {DB_TABLE}
        WHERE {WHERE_SQL} AND {SEARCH_COL}=1 AND {VEHICLE_COL} IS NOT NULL
        GROUP BY {VEHICLE_COL}
        ORDER BY searches DESC
        LIMIT 10
    """
    st.dataframe(run_query(q2, params))


def show_demographic():
    st.subheader("Driver age group with highest arrest rate")
    if not AGE_COL or not ARREST_COL:
        st.info("Age or arrest column not configured.")
        return
    q4 = f"""
        WITH binned AS (
          SELECT CASE
                   WHEN {AGE_COL} < 18 THEN '<18'
                   WHEN {AGE_COL} BETWEEN 18 AND 24 THEN '18-24'
                   WHEN {AGE_COL} BETWEEN 25 AND 34 THEN '25-34'
                   WHEN {AGE_COL} BETWEEN 35 AND 44 THEN '35-44'
                   WHEN {AGE_COL} BETWEEN 45 AND 54 THEN '45-54'
                   WHEN {AGE_COL} BETWEEN 55 AND 64 THEN '55-64'
                   ELSE '65+'
                 END AS age_group,
                 {ARREST_COL} AS arrested
          FROM {DB_TABLE}
          WHERE {WHERE_SQL}
        )
        SELECT age_group, COUNT(*) AS stops,
               SUM(arrested=1) AS arrests,
               ROUND(100*SUM(arrested=1)/COUNT(*),2) AS arrest_rate
        FROM binned
        GROUP BY age_group
        ORDER BY arrest_rate DESC
    """
    st.dataframe(run_query(q4, params))


def show_time():
    st.subheader("Time of day with most stops")
    if not TIME_COL:
        st.info("Time column not configured.")
        return
    q7 = f"""
        SELECT HOUR({TIME_COL}) AS hour_of_day, COUNT(*) AS stops
        FROM {DB_TABLE}
        WHERE {WHERE_SQL}
        GROUP BY hour_of_day
        ORDER BY stops DESC
    """
    st.dataframe(run_query(q7, params))


def show_violation():
    st.subheader("Violations with highest search & arrest rates")
    if not VIOLATION_COL:
        st.info("Violation column not configured.")
        return
    q10 = f"""
        SELECT {VIOLATION_COL} AS violation,
               COUNT(*) AS stops,
               SUM({SEARCH_COL}=1) AS searches,
               ROUND(100*SUM({SEARCH_COL}=1)/COUNT(*),2) AS search_rate,
               SUM({ARREST_COL}=1) AS arrests,
               ROUND(100*SUM({ARREST_COL}=1)/COUNT(*),2) AS arrest_rate
        FROM {DB_TABLE}
        WHERE {WHERE_SQL}
        GROUP BY {VIOLATION_COL}
        HAVING COUNT(*) >= 30
        ORDER BY arrest_rate DESC
        LIMIT 10
    """
    st.dataframe(run_query(q10, params))


def show_location():
    st.subheader("Countries with highest drug stop rate")
    if not COUNTRY_COL or not DRUGS_COL:
        st.info("Country or drug-related column not configured.")
        return
    q13 = f"""
        SELECT {COUNTRY_COL} AS country,
               COUNT(*) AS total_stops,
               SUM({DRUGS_COL}=1) AS drug_stops,
               ROUND(100*SUM({DRUGS_COL}=1)/COUNT(*),2) AS drug_rate
        FROM {DB_TABLE}
        WHERE {WHERE_SQL}
        GROUP BY {COUNTRY_COL}
        ORDER BY drug_rate DESC
        LIMIT 10
    """
    st.dataframe(run_query(q13, params))


def show_complex():
    st.subheader("Yearly breakdown of stops & arrests by country")
    if not DATE_COL or not COUNTRY_COL:
        st.info("Date or country column not configured.")
        return
    qC1 = f"""
        SELECT {COUNTRY_COL} AS country,
               YEAR({DATE_COL}) AS yr,
               COUNT(*) AS stops,
               SUM({ARREST_COL}=1) AS arrests
        FROM {DB_TABLE}
        WHERE {WHERE_SQL}
        GROUP BY {COUNTRY_COL}, YEAR({DATE_COL})
        ORDER BY country, yr
    """
    st.dataframe(run_query(qC1, params))


def show_sample():
    st.subheader("Sample Records")
    rows_sql = f"SELECT * FROM {DB_TABLE} WHERE {WHERE_SQL} LIMIT 200"
    st.dataframe(run_query(rows_sql, params))

# Route to the selected section
if section.startswith("🚗"):
    show_vehicle()
elif section.startswith("👥"):
    show_demographic()
elif section.startswith("⏱️"):
    show_time()
elif section.startswith("⚖️"):
    show_violation()
elif section.startswith("🗺️"):
    show_location()
elif section.startswith("🧠"):
    show_complex()
else:
    show_sample()

st.markdown("\n")
