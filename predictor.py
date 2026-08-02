"""
predictor.py
Predict next trading day OHLC values
"""

import logging
from concurrent.futures import ThreadPoolExecutor

from indicators import add_indicators
from feature_engineering import (
    create_features,
    create_targets,
)
from model import load_models
from config import MAX_WORKERS

logger = logging.getLogger(__name__)


# =====================================
# PREPARE ONE STOCK
# =====================================

def prepare_prediction_data(df):

    df = add_indicators(df)

    df = create_features(df)

    df = create_targets(df)

    return df


# =====================================
# PREDICT ONE STOCK
# =====================================

def predict_stock(symbol, df, models):

    try:

        df = prepare_prediction_data(df)

        feature_columns = models["features"]

        scaler = models["scaler"]

        latest = (
            df[feature_columns]
            .dropna()
            .tail(1)
        )

        if latest.empty:

            logger.warning(f"{symbol}: No valid prediction row")

            return None

        latest_scaled = scaler.transform(latest)

        open_price = models["open"].predict(latest_scaled)[0]

        high_price = models["high"].predict(latest_scaled)[0]

        low_price = models["low"].predict(latest_scaled)[0]

        close_price = models["close"].predict(latest_scaled)[0]

        prediction = {

            "Stock": symbol.replace(".NS", ""),

            "Open": round(float(open_price), 2),

            "High": round(float(high_price), 2),

            "Low": round(float(low_price), 2),

            "Close": round(float(close_price), 2),

        }

        return validate_prediction(prediction)

    except Exception as e:

        logger.exception(f"{symbol}: {e}")

        return None


# =====================================
# VALIDATE
# =====================================

def validate_prediction(pred):

    if pred is None:

        return None

    # High should be highest
    if pred["High"] < max(
        pred["Open"],
        pred["Close"],
        pred["Low"]
    ):
        pred["High"] = max(
            pred["Open"],
            pred["Close"],
            pred["Low"]
        )

    # Low should be lowest
    if pred["Low"] > min(
        pred["Open"],
        pred["Close"],
        pred["High"]
    ):
        pred["Low"] = min(
            pred["Open"],
            pred["Close"],
            pred["High"]
        )

    return pred


# =====================================
# PREDICT MULTIPLE STOCKS
# =====================================

def predict_multiple(stock_data):

    """
    stock_data =

    {
        "RELIANCE.NS": dataframe,
        "SBIN.NS": dataframe
    }
    """

    models = load_models()

    predictions = []

    with ThreadPoolExecutor(
        max_workers=MAX_WORKERS
    ) as executor:

        futures = [

            executor.submit(
                predict_stock,
                symbol,
                df,
                models
            )

            for symbol, df in stock_data.items()

        ]

        for future in futures:

            result = future.result()

            if result:

                predictions.append(result)

    return predictions
