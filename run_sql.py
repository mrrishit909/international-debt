"""Steps 2-4: load the IDS snapshot into DuckDB, run every sql/*.sql file, and write each result to results/<file name>.csv.

    ./venv/bin/python run_sql.py
"""
from pathlib import Path

import duckdb

HERE = Path(__file__).parent


def main():
    con = duckdb.connect()                                    # in memory: the snapshot is small
    con.execute(f"CREATE TABLE ids AS SELECT * FROM read_csv_auto('{HERE / 'data' / 'ids.csv.gz'}')")
    con.execute(f"CREATE TABLE countries AS SELECT * FROM read_csv_auto('{HERE / 'data' / 'countries.csv'}')")
    for f in sorted((HERE / "sql").glob("*.sql")):
        out = HERE / "results" / f"{f.stem}.csv"
        con.execute(f.read_text()).fetchdf().to_csv(out, index=False)
        print(f"{f.name:30s} -> {out.name}")


if __name__ == "__main__":
    main()
