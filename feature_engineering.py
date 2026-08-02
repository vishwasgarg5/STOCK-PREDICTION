"""
feature_engineering.py
Create ML features and target variables
"""

import pandas as pd

# Number of lag features
N_LAGS = 10


def create_features(df: pd.DataFrame):
    """
    Create machine learning features
    """

    df = df.copy()

    # -----------------------------
    # Lag Features
    # -----------------------------
    for lag in range(1, N_LAGS + 1):
        df[f"CLOSE_LAG_{lag}"] = df["Close"].shift(lag)

    # -----------------------------
    # Rolling Statistics
    # -----------------------------
    df["ROLL_MEAN_5"] = df["Close"].rolling(5).mean()
    df["ROLL_MEAN_10"] = df["Close"].rolling(10).mean()

    df["ROLL_STD_5"] = df["Close"].rolling(5).std()
    df["ROLL_STD_10"] = df["Close"].rolling(10).std()

    # -----------------------------
    # Price Spread
    # -----------------------------
    df["HIGH_LOW_SPREAD"] = df["High"] - df["Low"]

    df["OPEN_CLOSE_SPREAD"] = (
        df["Close"] - df["Open"]
    )

    return df


def create_targets(df: pd.DataFrame):
    """
    Next trading day targets
    """

    df = df.copy()

    df["TARGET_OPEN"] = df["Open"].shift(-1)
    df["TARGET_HIGH"] = df["High"].shift(-1)
    df["TARGET_LOW"] = df["Low"].shift(-1)
    df["TARGET_CLOSE"] = df["Close"].shift(-1)

    return df


def prepare_dataset(df):
    """
    Prepare dataset for training and prediction
    """

    df = df.copy()

    # Keep last row for prediction
    prediction_df = df.tail(1).copy()

    # Remove rows with NaN values
    train_df = df.dropna().copy()

    target_columns = [
        "TARGET_OPEN",
        "TARGET_HIGH",
        "TARGET_LOW",
        "TARGET_CLOSE",
    ]

    feature_columns = [
        col
        for col in train_df.columns
        if col not in target_columns
    ]

    X = train_df[feature_columns]

    y = {
        "open": train_df["TARGET_OPEN"],
        "high": train_df["TARGET_HIGH"],
        "low": train_df["TARGET_LOW"],
        "close": train_df["TARGET_CLOSE"],
    }

    return (
        X,
        y,
        feature_columns,
        prediction_df
    )
