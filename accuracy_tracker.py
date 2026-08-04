"""
accuracy_tracker.py
Evaluate prediction accuracy
"""

import os
import pandas as pd
import yfinance as yf
from datetime import timedelta
from sklearn.metrics import mean_absolute_error

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

def get_actual_price(symbol, prediction_date):
    """
    Download the actual OHLC for the prediction date.
    Returns None if data is unavailable.
    """

    try:

        start = pd.to_datetime(prediction_date)

        end = start + timedelta(days=5)

        df = yf.download(
            symbol + ".NS",
            start=start.strftime("%Y-%m-%d"),
            end=end.strftime("%Y-%m-%d"),
            progress=False,
            auto_adjust=False,
        )

        if df.empty:
            return None

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        row = df.iloc[0]

        return {
            "Open": float(row["Open"]),
            "High": float(row["High"]),
            "Low": float(row["Low"]),
            "Close": float(row["Close"]),
        }

    except Exception:
        return None
def evaluate_prediction(predicted, actual):

    return {
        "MAE_Open": round(
            mean_absolute_error(
                [actual["Open"]],
                [predicted["Open"]]
            ),
            2
        ),

        "MAE_High": round(
            mean_absolute_error(
                [actual["High"]],
                [predicted["High"]]
            ),
            2
        ),

        "MAE_Low": round(
            mean_absolute_error(
                [actual["Low"]],
                [predicted["Low"]]
            ),
            2
        ),

        "MAE_Close": round(
            mean_absolute_error(
                [actual["Close"]],
                [predicted["Close"]]
            ),
            2
        )
    }
