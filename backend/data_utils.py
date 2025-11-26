import re
import pandas as pd
from pathlib import Path

CSV_PATH = Path(__file__).parent / "top_100_saas_companies_2025.csv"


def _parse_money(value):
    """
    Convert strings like "$2.5B", "300M", "1,200,000" into floats (USD).
    Returns None if parsing fails.
    """
    if pd.isna(value):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    if not s:
        return None
    s = s.replace("$", "").replace(",", "").strip()

    # IMPORTANT: single \s here (the old code used \\s, which breaks the regex)
    m = re.match(r"([0-9.]+)\s*([KMBT]?)", s, re.IGNORECASE)
    if not m:
        return None
    num = float(m.group(1))
    suffix = m.group(2).upper()
    multiplier = {
        "": 1.0,
        "K": 1e3,
        "M": 1e6,
        "B": 1e9,
        "T": 1e12,
    }.get(suffix, 1.0)
    return num * multiplier


def load_saas_df() -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH)

    # Normalize numeric fields
    if "ARR" in df.columns:
        df["ARR_num"] = df["ARR"].apply(_parse_money).astype(float)
    if "Valuation" in df.columns:
        df["Valuation_num"] = df["Valuation"].apply(_parse_money).astype(float)
    if "Total Funding" in df.columns:
        df["Total_Funding_num"] = df["Total Funding"].apply(_parse_money).astype(float)

    if "Employees" in df.columns:
        df["Employees_num"] = (
            df["Employees"]
            .astype(str)
            .str.replace(",", "", regex=False)
            .apply(lambda x: float(x) if x.replace(".", "", 1).isdigit() else None)
            .astype(float)
        )

    return df
