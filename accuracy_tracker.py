"""
accuracy_tracker.py
Evaluate prediction accuracy
"""

import os
import pandas as pd

from config import REPORT_DIR

PREDICTION_FILE = os.path.join(
    REPORT_DIR,
    "prediction_history.csv"
)

ACCURACY_FILE = os.path.join(
    REPORT_DIR,
    "accuracy_history.csv"
)


def load_prediction_history():

    if not os.path.exists(PREDICTION_FILE):
        return None

    return pd.read_csv(PREDICTION_FILE)


def save_accuracy(result):

    df = pd.DataFrame([result])

    if os.path.exists(ACCURACY_FILE):

        old = pd.read_csv(ACCURACY_FILE)

        df = pd.concat(
            [old, df],
            ignore_index=True
        )

    df.to_csv(
        ACCURACY_FILE,
        index=False
    )

    print("Accuracy history updated.")
