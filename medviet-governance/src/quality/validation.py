import pandas as pd
import great_expectations as gx
from great_expectations.core.expectation_suite import ExpectationSuite


def build_patient_expectation_suite() -> ExpectationSuite:
    context = gx.get_context()
    suite_name = "patient_data_suite"

    try:
        suite = context.add_expectation_suite(suite_name)
    except Exception:
        suite = context.get_expectation_suite(suite_name)

    df = pd.read_csv("data/raw/patients_raw.csv")
    validator = context.sources.pandas_default.read_dataframe(df)

    validator.expect_column_values_to_not_be_null("patient_id")
    validator.expect_column_value_lengths_to_equal(column="cccd", value=12)
    validator.expect_column_values_to_be_between(column="ket_qua_xet_nghiem", min_value=0, max_value=50)

    valid_conditions = ["Tiểu đường", "Huyết áp cao", "Tim mạch", "Khỏe mạnh"]
    validator.expect_column_values_to_be_in_set(column="benh", value_set=valid_conditions)
    validator.expect_column_values_to_match_regex(column="email", regex=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    validator.expect_column_values_to_be_unique(column="patient_id")

    validator.save_expectation_suite()
    return suite


def validate_anonymized_data(filepath: str) -> dict:
    df = pd.read_csv(filepath)
    raw_df = pd.read_csv("data/raw/patients_raw.csv")

    results = {
        "success": True,
        "failed_checks": [],
        "stats": {
            "total_rows": len(df),
            "columns": list(df.columns),
        },
    }

    if "cccd" in df.columns and "cccd" in raw_df.columns:
        overlap = set(df["cccd"].astype(str)).intersection(set(raw_df["cccd"].astype(str)))
        if overlap:
            results["success"] = False
            results["failed_checks"].append("Some anonymized CCCD values still match raw input")

    required_columns = ["patient_id", "ho_ten", "cccd", "so_dien_thoai", "email"]
    missing_nulls = [col for col in required_columns if col in df.columns and df[col].isnull().any()]
    if missing_nulls:
        results["success"] = False
        results["failed_checks"].append(f"Null values found in required columns: {missing_nulls}")

    if len(df) != len(raw_df):
        results["success"] = False
        results["failed_checks"].append(
            f"Row count mismatch: anonymized={len(df)}, original={len(raw_df)}"
        )

    return results
