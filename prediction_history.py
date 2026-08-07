"""
prediction_history.py

Save daily AI stock predictions to history.
"""

import os
import pandas as pd

from config import REPORT_DIR


# ==========================================
# FILE
# ==========================================

HISTORY_FILE = os.path.join(
    REPORT_DIR,
    "prediction_history.csv"
)


# ==========================================
# SAVE PREDICTION HISTORY
# ==========================================

def save_prediction_history(
    predictions,
    prediction_date
):
    """
    Save today's predictions.

    Columns:
        Prediction_Date
        Stock
        Open
        High
        Low
        Close
    """

    if not predictions:
        print("No predictions to save.")
        return

    os.makedirs(
        REPORT_DIR,
        exist_ok=True
    )

    df = pd.DataFrame(predictions)

    # --------------------------------------
    # Add prediction date
    # --------------------------------------

    df.insert(
        0,
        "Prediction_Date",
        prediction_date
    )

    # --------------------------------------
    # Required columns
    # --------------------------------------

    required_columns = [
        "Prediction_Date",
        "Stock",
        "Open",
        "High",
        "Low",
        "Close"
    ]

    missing = [
        col
        for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing prediction columns: {missing}"
        )

    df = df[
        required_columns
    ]

    # --------------------------------------
    # Remove duplicate prediction
    # --------------------------------------
    # If the workflow is manually triggered
    # twice on the same day, don't duplicate
    # the same stock prediction.

    if os.path.exists(HISTORY_FILE):

        old = pd.read_csv(
            HISTORY_FILE
        )

        old = old[
            ~(
                (old["Prediction_Date"].astype(str) == str(prediction_date))
                &
                (old["Stock"].astype(str).isin(
                    df["Stock"].astype(str)
                ))
            )
        ]

        df = pd.concat(
            [
                old,
                df
            ],
            ignore_index=True
        )

    # --------------------------------------
    # Save
    # --------------------------------------

    df.to_csv(
        HISTORY_FILE,
        index=False
    )

    print(
        f"Prediction history updated: {HISTORY_FILE}"
    )


# ==========================================
# LOAD PREDICTION HISTORY
# ==========================================

def load_prediction_history():

    if not os.path.exists(
        HISTORY_FILE
    ):
        return pd.DataFrame()

    return pd.read_csv(
        HISTORY_FILE
    )
