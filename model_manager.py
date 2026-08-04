"""
model_manager.py
Compare candidate model with existing model
"""

import os
import pandas as pd

from config import REPORT_DIR


MODEL_HISTORY = os.path.join(
    REPORT_DIR,
    "model_history.csv"
)


def load_history():

    if not os.path.exists(MODEL_HISTORY):

        return None

    return pd.read_csv(
        MODEL_HISTORY
    )


def get_previous_metrics(model_name):

    df = load_history()

    if df is None:
        return None

    df = df[
        df["Model"] == model_name.upper()
    ]

    # Need at least 2 records
    # because latest record is the new model

    if len(df) < 2:

        return None

    return df.iloc[-2]


def get_latest_metrics(model_name):

    df = load_history()

    if df is None:
        return None

    df = df[
        df["Model"] == model_name.upper()
    ]

    if df.empty:

        return None

    return df.iloc[-1]


def should_replace(model_name):

    old = get_previous_metrics(
        model_name
    )

    new = get_latest_metrics(
        model_name
    )


    if old is None or new is None:

        return False


    # Lower MAE is better

    if new["MAE"] < old["MAE"]:

        return True


    return False
