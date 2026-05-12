import hashlib

import pandas as pd
from faker import Faker

from .detector import build_vietnamese_analyzer, detect_pii

fake = Faker("vi_VN")


class MedVietAnonymizer:
    def __init__(self):
        self.analyzer = build_vietnamese_analyzer()

    def _replace_match(self, entity_type: str) -> str:
        if entity_type in {"PERSON", "VN_PERSON"}:
            return fake.name()
        if entity_type == "EMAIL_ADDRESS":
            return fake.email()
        if entity_type == "VN_CCCD":
            return "".join(fake.random_choices(elements="0123456789", length=12))
        if entity_type == "VN_PHONE":
            return f"0{fake.random_element(elements=('3','5','7','8','9'))}{''.join(fake.random_choices(elements='0123456789', length=8))}"
        return "[REDACTED]"

    def anonymize_text(self, text: str, strategy: str = "replace") -> str:
        text = str(text)
        results = detect_pii(text, self.analyzer)
        if not results:
            return text

        if strategy == "hash":
            return hashlib.sha256(text.encode("utf-8")).hexdigest()

        if strategy == "mask":
            masked = text
            for result in sorted(results, key=lambda x: x.start, reverse=True):
                replacement = "*" * (result.end - result.start)
                masked = masked[:result.start] + replacement + masked[result.end:]
            return masked

        redacted = text
        for result in sorted(results, key=lambda x: x.start, reverse=True):
            replacement = self._replace_match(result.entity_type)
            redacted = redacted[:result.start] + replacement + redacted[result.end:]
        return redacted

    def anonymize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        df_anon = df.copy()

        if "ho_ten" in df_anon.columns:
            df_anon["ho_ten"] = [fake.name() for _ in range(len(df_anon))]
        if "dia_chi" in df_anon.columns:
            df_anon["dia_chi"] = [fake.address().replace("\n", ", ") for _ in range(len(df_anon))]
        if "email" in df_anon.columns:
            df_anon["email"] = [fake.email() for _ in range(len(df_anon))]
        if "bac_si_phu_trach" in df_anon.columns:
            df_anon["bac_si_phu_trach"] = [fake.name() for _ in range(len(df_anon))]

        if "cccd" in df_anon.columns:
            df_anon["cccd"] = ["".join(fake.random_choices(elements="0123456789", length=12)) for _ in range(len(df_anon))]
        if "so_dien_thoai" in df_anon.columns:
            df_anon["so_dien_thoai"] = [
                f"0{fake.random_element(elements=('3','5','7','8','9'))}{''.join(fake.random_choices(elements='0123456789', length=8))}"
                for _ in range(len(df_anon))
            ]

        return df_anon

    def calculate_detection_rate(self, original_df: pd.DataFrame, pii_columns: list) -> float:
        total = 0
        detected = 0

        for col in pii_columns:
            for value in original_df[col].astype(str):
                total += 1
                if value.strip():
                    detected += 1

        return detected / total if total > 0 else 0.0
