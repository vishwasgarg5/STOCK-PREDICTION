"""
feature_engineering.py
Feature Engineering for AI NSE Stock Prediction
"""

import pandas as pd

N_LAGS = 10


# ======================================================
# CREATE FEATURES
# ======================================================

def create_features(df):

    df = df.copy()

    # -------------------------
    # Lag Features
    # -------------------------
    for lag in range(1, N_LAGS + 1):
        df[f"CLOSE_LAG_{lag}"] = df["Close"].shift(lag)

    # -------------------------
    # Rolling Mean
    # -------------------------
    df["ROLL_MEAN_5"] = df["Close"].rolling(5).mean()
    df["ROLL_MEAN_10"] = df["Close"].rolling(10).mean()

    # -------------------------
    # Rolling Std
    # -------------------------
    df["ROLL_STD_5"] = df["Close"].rolling(5).std()
    df["ROLL_STD_10"] = df["Close"].rolling(10).std()

    # -------------------------
    # Price Spread
    # -------------------------
    df["HIGH_LOW_SPREAD"] = df["High"] - df["Low"]

    df["OPEN_CLOSE_SPREAD"] = (
        df["Close"] - df["Open"]
    )

    return df


# ======================================================
# CREATE TARGETS
# ======================================================

def create_targets(df):

    df = df.copy()

    df["TARGET_OPEN"] = df["Open"].shift(-1)
    df["TARGET_HIGH"] = df["High"].shift(-1)
    df["TARGET_LOW"] = df["Low"].shift(-1)
    df["TARGET_CLOSE"] = df["Close"].shift(-1)

    return df


# ======================================================
# FEATURE LIST
# ======================================================

def get_feature_columns():

    features = [

        # OHLCV

        "Open",
        "High",
        "Low",
        "Close",
        "Volume",

        # Indicators

        "EMA20",
        "EMA50",

        "RSI",

        "MACD",
        "MACD_SIGNAL",

        "ADX",

        "ATR",

        "OBV",

        "RETURN_1",
        "RETURN_5",

        "VOLATILITY",

        # Engineered

        "HIGH_LOW_SPREAD",

        "OPEN_CLOSE_SPREAD",

        "ROLL_MEAN_5",
        "ROLL_MEAN_10",

        "ROLL_STD_5",
        "ROLL_STD_10",

    ]

    for lag in range(1, N_LAGS + 1):

        features.append(f"CLOSE_LAG_{lag}")

    return features


# ======================================================
# PREPARE DATASET
# ======================================================

def prepare_dataset(df):

    df = df.copy()

    feature_columns = get_feature_columns()

    target_columns = [

        "TARGET_OPEN",
        "TARGET_HIGH",
        "TARGET_LOW",
        "TARGET_CLOSE"

    ]

    train_df = df.dropna(
        subset=feature_columns + target_columns
    )

    prediction_df = (
        df[feature_columns]
        .dropna()
        .tail(1)
    )

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
