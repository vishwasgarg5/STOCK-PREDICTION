"""
predictor.py
Predict next trading day OHLC values
"""

import logging
from concurrent.futures import ThreadPoolExecutor

from indicators import add_indicators
from feature_engineering import create_features
from model import load_models
from config import MAX_WORKERS

logger = logging.getLogger(__name__)


# =====================================================
# PREPARE DATA
# =====================================================

def prepare_prediction_data(df):

    df = add_indicators(df)

    df = create_features(df)

    # Prediction should NOT create target columns

    return df


# =====================================================
# VALIDATE PREDICTION
# =====================================================

def validate_prediction(pred):

    pred["High"] = max(
        pred["High"],
        pred["Open"],
        pred["Close"],
        pred["Low"]
    )

    pred["Low"] = min(
        pred["Low"],
        pred["Open"],
        pred["Close"],
        pred["High"]
    )

    return pred


# =====================================================
# PREDICT ONE STOCK
# =====================================================

def predict_stock(symbol, df, loaded):

    try:

        df = prepare_prediction_data(df)

        feature_columns = loaded["features"]

        scaler = loaded["scaler"]

        models = loaded["models"]

        missing = [c for c in feature_columns if c not in df.columns]

        if missing:

            logger.error(f"{symbol}: Missing Features -> {missing}")

            return None

        latest = df[feature_columns].dropna().tail(1)

        if latest.empty:

            logger.warning(f"{symbol}: No valid feature row")

            return None

        latest_scaled = scaler.transform(latest)

        prediction = {

            "Stock": symbol.replace(".NS", ""),

            "Open": round(
                float(models["open"].predict(latest_scaled)[0]),
                2
            ),

            "High": round(
                float(models["high"].predict(latest_scaled)[0]),
                2
            ),

            "Low": round(
                float(models["low"].predict(latest_scaled)[0]),
                2
            ),

            "Close": round(
                float(models["close"].predict(latest_scaled)[0]),
                2
            ),

        }

        return validate_prediction(prediction)

    except Exception as e:

        logger.exception(f"{symbol}: {e}")

        return None


# =====================================================
# PREDICT MULTIPLE STOCKS
# =====================================================

def predict_multiple(stock_data):

    loaded = load_models()

    predictions = []

    with ThreadPoolExecutor(
        max_workers=MAX_WORKERS
    ) as executor:

        futures = [

            executor.submit(
                predict_stock,
                symbol,
                df,
                loaded
            )

            for symbol, df in stock_data.items()

        ]

        for future in futures:

            result = future.result()

            if result:

                predictions.append(result)

    logger.info(f"Generated {len(predictions)} predictions")

    return predictions
