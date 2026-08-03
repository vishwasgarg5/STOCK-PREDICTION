"""
feature_engineering.py
Create ML features and target variables
"""

import pandas as pd

N_LAGS = 10


def create_features(df):

    df = df.copy()

    # Lag Features
    for lag in range(1, N_LAGS + 1):
        df[f"CLOSE_LAG_{lag}"] = df["Close"].shift(lag)

    # Rolling Features
    df["ROLL_MEAN_5"] = df["Close"].rolling(5).mean()
    df["ROLL_MEAN_10"] = df["Close"].rolling(10).mean()

    df["ROLL_STD_5"] = df["Close"].rolling(5).std()
    df["ROLL_STD_10"] = df["Close"].rolling(10).std()

    # Price Features
    df["HIGH_LOW_SPREAD"] = df["High"] - df["Low"]
    df["OPEN_CLOSE_SPREAD"] = df["Close"] - df["Open"]

    return df


def create_targets(df):

    df = df.copy()

    df["TARGET_OPEN"] = df["Open"].shift(-1)
    df["TARGET_HIGH"] = df["High"].shift(-1)
    df["TARGET_LOW"] = df["Low"].shift(-1)
    df["TARGET_CLOSE"] = df["Close"].shift(-1)

    return df


def prepare_dataset(df):

    df = df.copy()

    target_columns = [
        "TARGET_OPEN",
        "TARGET_HIGH",
        "TARGET_LOW",
        "TARGET_CLOSE",
    ]

    # Explicit feature list
    feature_columns = [

        "Open",
        "High",
        "Low",
        "Close",
        "Volume",

        "RSI",
        "MACD",
        "MACD_SIGNAL",

        "EMA20",
        "EMA50",

        "ADX",
        "ATR",

        "HIGH_LOW_SPREAD",
        "OPEN_CLOSE_SPREAD",

        "ROLL_MEAN_5",
        "ROLL_MEAN_10",

        "ROLL_STD_5",
        "ROLL_STD_10",

    ]

    for lag in range(1, N_LAGS + 1):
        feature_columns.append(f"CLOSE_LAG_{lag}")

    # Drop only rows missing required columns
    train_df = df.dropna(
        subset=feature_columns + target_columns
    )

    prediction_df = df[feature_columns].dropna().tail(1)

    X = train_df[feature_columns]

    y = {

        "open": train_df["TARGET_OPEN"],

        "high": train_df["TARGET_HIGH"],

        "low": train_df["TARGET_LOW"],

        "close": train_df["TARGET_CLOSE"],

    }

    return X, y, feature_columns, prediction_df
