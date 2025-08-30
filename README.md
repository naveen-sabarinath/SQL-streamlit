# Police Traffic Stops — SQL‑Only Streamlit Dashboard

A lightweight, **SQL‑first** Streamlit app that explores police traffic‑stop records directly from **MySQL** using parameterized queries (no ORM models). The UI provides filters and ready‑made tables for vehicles, demographics, violations, time patterns, and locations.

> Built with: Streamlit · pandas · SQLAlchemy (MySQL + PyMySQL)

---

## ✨ Features

- **End‑to‑end filters** (date range, country, gender, race, violation + boolean toggles for search/arrest/drugs)
- **Prebuilt tables** for:
  - Top vehicles in drug‑related stops & most‑searched vehicles
  - Arrest rate by age group
  - Time‑of‑day distribution of stops
  - Violation‑level search & arrest rates
  - Country‑level drug‑stop rate
  - Yearly breakdown of stops & arrests by country
  - Sample records view
- **KPI cards**: total stops, arrest rate, search rate, drug‑related rate
- **Pure SQL** queries (fast to reason about; easy to port to other warehouses)
- **Caching** for connection + query results to keep the UI snappy

The app reads MySQL directly and expects a table named **`police`** inside a database **`traffic_stops`**. Configuration lives at the top of `app.py` (DB creds, table/column names).

---

## 🗂 Repository Layout

```
.
├── app.py                           # Streamlit app (SQL-first dashboard)
├── data.ipynb                       # (Optional) Notebook for EDA / experiments
├── traffic_stops - traffic_stops_with_vehicle_number.csv  # Example dataset
└── README.md
```

> The Streamlit app connects to MySQL via SQLAlchemy + PyMySQL, renders KPI cards, and shows multiple tabular sections using parameterized raw SQL.


---

## 🚀 Quickstart

### 1) Python environment
```bash
# Using venv (Python 3.10+ recommended)
python -m venv .venv
source .venv/bin/activate   # on Windows: .venv\Scripts\activate

pip install --upgrade pip
pip install streamlit pandas sqlalchemy pymysql
```

> If you prefer, create a `requirements.txt` with:
> ```txt
> streamlit
> pandas
> SQLAlchemy
> PyMySQL
> ```

### 2) MySQL setup

Create a database and user (adjust as needed):

```sql
CREATE DATABASE traffic_stops CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
CREATE USER 'root'@'localhost' IDENTIFIED BY 'root';  -- or your own user/pass
GRANT ALL PRIVILEGES ON traffic_stops.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
```

Create the `police` table (baseline schema suggestion — adapt to your CSV):
```sql
USE traffic_stops;

CREATE TABLE police (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  stop_date DATETIME NULL,
  stop_time TIME NULL,
  country_name VARCHAR(64),
  driver_gender VARCHAR(8),
  driver_race VARCHAR(64),
  violation VARCHAR(128),
  search_conducted TINYINT(1),
  is_arrested TINYINT(1),
  drugs_related_stop TINYINT(1),
  vehicle_number VARCHAR(64),
  driver_age INT
);

-- Helpful indexes for the UI filters/queries
CREATE INDEX idx_police_stopdate   ON police (stop_date);
CREATE INDEX idx_police_country    ON police (country_name);
CREATE INDEX idx_police_gender     ON police (driver_gender);
CREATE INDEX idx_police_race       ON police (driver_race);
CREATE INDEX idx_police_violation  ON police (violation);
CREATE INDEX idx_police_search     ON police (search_conducted);
CREATE INDEX idx_police_arrest     ON police (is_arrested);
CREATE INDEX idx_police_drugs      ON police (drugs_related_stop);
```

### 3) Load data

#### Option A — SQL `LOAD DATA` (fastest)
```sql
LOAD DATA LOCAL INFILE '/absolute/path/to/traffic_stops_with_vehicle_number.csv'
INTO TABLE police
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(@stop_date, @stop_time, @country_name, @driver_gender, @driver_race, @violation,
 @search_conducted, @is_arrested, @drugs_related_stop, @vehicle_number, @driver_age)
SET
  stop_date = NULLIF(@stop_date,''),
  stop_time = NULLIF(@stop_time,''),
  country_name = NULLIF(@country_name,''),
  driver_gender = NULLIF(@driver_gender,''),
  driver_race = NULLIF(@driver_race,''),
  violation = NULLIF(@violation,''),
  search_conducted = NULLIF(@search_conducted,''),
  is_arrested = NULLIF(@is_arrested,''),
  drugs_related_stop = NULLIF(@drugs_related_stop,''),
  vehicle_number = NULLIF(@vehicle_number,''),
  driver_age = NULLIF(@driver_age,'');
```

> You may need to allow local infile: `SET GLOBAL local_infile=1;` and add `--local-infile=1` to your MySQL client.

#### Option B — Python (pandas)
```python
import pandas as pd
from sqlalchemy import create_engine

csv = "traffic_stops - traffic_stops_with_vehicle_number.csv"
engine = create_engine("mysql+pymysql://root:root@localhost:3306/traffic_stops?charset=utf8mb4")

df = pd.read_csv(csv)
df.to_sql("police", engine, if_exists="append", index=False, chunksize=10_000)
```

### 4) Configure the app

Open `app.py` and adjust the config block at the top if needed:

```python
DB_USER  = "root"
DB_PASS  = "root"
DB_HOST  = "localhost"
DB_PORT  = 3306
DB_NAME  = "traffic_stops"
DB_TABLE = "police"
# Column names (edit to your schema)
DATE_COL      = "stop_date"
TIME_COL      = "stop_time"
COUNTRY_COL   = "country_name"
GENDER_COL    = "driver_gender"
RACE_COL      = "driver_race"
VIOLATION_COL = "violation"
SEARCH_COL    = "search_conducted"
ARREST_COL    = "is_arrested"
DRUGS_COL     = "drugs_related_stop"
VEHICLE_COL   = "vehicle_number"
AGE_COL       = "driver_age"
```

> **Tip:** You can convert these to environment variables if you prefer secrets outside source control. For example:
> ```python
> import os
> DB_USER = os.getenv("DB_USER", "root")
> DB_PASS = os.getenv("DB_PASS", "root")
> ```

### 5) Run

```bash
streamlit run app.py
```

The app will start on `http://localhost:8501/` by default.

---

## 🧭 How to Use

- Use the **sidebar** to set filters (date range, country/gender/race/violation; toggle search/arrest/drug‑related).
- Navigate through sections: **Vehicle‑Based**, **Demographic**, **Time & Duration**, **Violation**, **Location**, **Complex**, **Sample Records**.
- KPI cards at the top summarize the current filter state.
- All tables are **server‑side SQL** queries with safe parameters; performance benefits from the indexes defined above.

---

## 🛠 Tech Notes

- **Connection**: `mysql+pymysql` via SQLAlchemy; connection & queries cached with Streamlit cache decorators.
- **Safety**: App builds `WHERE` clauses with named parameters to avoid SQL injection; multiselects create `IN (...)` safely.
- **Performance**: Avoid `SELECT *` for heavy browsing; consider column pruning or materialized summaries for large datasets.
- **Charts**: This is intentionally **tables‑only**. You can add charts later with `st.bar_chart` or build aggregated SQL and plot with matplotlib/altair.

---

## 📒 Notebook (optional)

`data.ipynb` can be used for quick EDA or preprocessing before loading to MySQL. Open it in Jupyter or VS Code and adapt to your dataset.

---

## 🤝 Contributing

1. Fork the repo & create a feature branch.
2. Keep PRs focused (one change/theme).
3. Add helpful docstrings/comments for any SQL or UI change.
4. If you add columns or rename fields, update the config block at the top of `app.py` and README instructions.

---

## 🧪 Troubleshooting

- **Cannot connect to MySQL**: Check host/port and user privileges. Verify `mysql --host localhost --port 3306 -u root -p` works.
- **No rows displayed**: Filter too strict; clear filters. Confirm data is loaded into the `police` table.
- **Datetime parsing**: Ensure CSV date/time formats match the DDL; adjust `LOAD DATA` or pandas parsing as needed.
- **Local infile errors**: Enable `local_infile` and restart MySQL server if using Option A.
- **Large CSV**: Use `chunksize` in `to_sql`, or `LOAD DATA` for better performance.

---

## 📄 License

This project is released under the MIT License. See `LICENSE` (add one if missing).

---

## 🙌 Acknowledgements

Thanks to open data initiatives that make traffic‑stop datasets publicly available and reproducible for learning and analysis.
