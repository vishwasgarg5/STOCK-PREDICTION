"""
prediction_history.py
Save daily predictions to history
"""

import os
import pandas as pd

from config import REPORT_DIR


HISTORY_FILE = os.path.join(
    REPORT_DIR,
    "prediction_history.csv"
)


def save_prediction_history(predictions, prediction_date):

    if not predictions:
        return

    # Create reports directory if required
    os.makedirs(REPORT_DIR, exist_ok=True)

    df = pd.DataFrame(predictions)

    df.insert(
        0,
        "Prediction_Date",
        prediction_date
    )

    if os.path.exists(HISTORY_FILE):

        old = pd.read_csv(HISTORY_FILE)

        df = pd.concat(
            [old, df],
            ignore_index=True
        )

    df.to_csv(
        HISTORY_FILE,
        index=False
    )

    print(
        f"Prediction history updated: {HISTORY_FILE}"
    )
