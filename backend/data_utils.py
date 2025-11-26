from __future__ import annotations

import re
from pathlib import Path
from typing import List, Dict

import pandas as pd

from config import DATASET_PATH

MONEY_RE = re.compile(r"^\s*\$?\s*([\d,.]+)\s*([KMBT]?)\s*$", re.IGNORECASE)


def _parse_money(value):
    """Parse money-like strings such as "$3T", "65.4M", "1,200" into floats.

    This is generic and works for any column that stores money-ish values.
    Returns None if parsing fails.
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    if not s:
        return None
    m = MONEY_RE.match(s)
    if not m:
        return None
    num_str, suffix = m.groups()
    try:
        num = float(num_str.replace(",", ""))
    except ValueError:
        return None
    multiplier = {
        "": 1.0,
        "K": 1e3,
        "M": 1e6,
        "B": 1e9,
        "T": 1e12,
    }.get(suffix.upper(), 1.0)
    return num * multiplier


def _enrich_numeric_from_strings(df: pd.DataFrame) -> pd.DataFrame:
    """Add *_num numeric columns for string columns that look numeric or money-like.

    This is dataset-agnostic: it just inspects values.
    """
    for col in list(df.columns):
        series = df[col]
        if not pd.api.types.is_object_dtype(series):
            continue

        non_null = series.dropna().astype(str)
        if non_null.empty:
            continue

        sample = non_null.sample(min(len(non_null), 50), random_state=0)

        # Try money-like parsing first
        parsed_money = sample.map(_parse_money)
        money_ratio = parsed_money.notna().mean()

        new_col_name = f"{col}_num"
        if money_ratio >= 0.6:
            full_parsed = series.dropna().astype(str).map(_parse_money)
            df[new_col_name] = full_parsed
            continue

        # Try plain numeric with commas
        cleaned = sample.str.replace(",", "", regex=False)
        parsed_numeric = pd.to_numeric(cleaned, errors="coerce")
        numeric_ratio = parsed_numeric.notna().mean()
        if numeric_ratio >= 0.6:
            full_cleaned = series.dropna().astype(str).str.replace(",", "", regex=False)
            df[new_col_name] = pd.to_numeric(full_cleaned, errors="coerce")

    return df


def load_dataset(path: Path | None = None) -> pd.DataFrame:
    """Load the CSV dataset and enrich it with generic numeric columns.

    The function is general and works for any CSV file.
    """
    csv_path = path or DATASET_PATH
    df = pd.read_csv(csv_path)
    df = _enrich_numeric_from_strings(df)
    return df


def build_schema(df: pd.DataFrame) -> List[Dict]:
    """Build a simple schema describing the dataframe.

    Each schema entry has:
    - name: column name
    - kind: 'number', 'integer', 'string', or 'datetime'
    - examples: up to 3 example values as strings
    """
    schema: List[Dict] = []
    for col in df.columns:
        series = df[col]
        if pd.api.types.is_integer_dtype(series):
            kind = "integer"
        elif pd.api.types.is_numeric_dtype(series):
            kind = "number"
        elif pd.api.types.is_datetime64_any_dtype(series):
            kind = "datetime"
        else:
            kind = "string"

        examples = series.dropna().astype(str).unique()[:3].tolist()
        schema.append(
            {
                "name": col,
                "kind": kind,
                "examples": examples,
            }
        )
    return schema
