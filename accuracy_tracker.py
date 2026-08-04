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

def evaluate_prediction_file(prediction_date):

    history = load_prediction_history()

    if history is None:
        return

    history = history[
        history["Prediction_Date"] == prediction_date
    ]

    if history.empty:
        return

    results = []

    for _, row in history.iterrows():

        actual = get_actual_price(
            row["Stock"],
            prediction_date
        )

        if actual is None:
            continue

        predicted = {
            "Open": row["Open"],
            "High": row["High"],
            "Low": row["Low"],
            "Close": row["Close"],
        }

        score = evaluate_prediction(
            predicted,
            actual
        )

        score["Date"] = prediction_date
        score["Stock"] = row["Stock"]

        results.append(score)

    if not results:
        return

    df = pd.DataFrame(results)

    summary = {

        "Date": prediction_date,

        "Stocks": len(df),

        "MAE_Open": round(df["MAE_Open"].mean(), 2),

        "MAE_High": round(df["MAE_High"].mean(), 2),

        "MAE_Low": round(df["MAE_Low"].mean(), 2),

        "MAE_Close": round(df["MAE_Close"].mean(), 2),

    }

    save_accuracy(summary)

    print(summary)
