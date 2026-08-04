"""
model_manager.py
Compare model performance
"""

import pandas as pd

from config import REPORT_DIR


MODEL_HISTORY = (
    REPORT_DIR +
    "/model_history.csv"
)


def get_latest_metrics(model_name):

    df = pd.read_csv(
        MODEL_HISTORY
    )

    df = df[
        df["Model"] == model_name.upper()
    ]

    if df.empty:
        return None

    return df.iloc[-1]


def compare_models(
        old_mae,
        new_mae
):

    if new_mae < old_mae:

        return "REPLACE"

    else:

        return "KEEP"
