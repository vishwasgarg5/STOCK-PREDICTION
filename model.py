"""
model.py
Optimized XGBoost Model Training & Loading
"""

import os
import joblib
import logging
import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

from xgboost import XGBRegressor

from config import (
    MODEL_DIR,
    RANDOM_STATE,
    TEST_SIZE,
    N_ESTIMATORS,
    MAX_DEPTH,
    LEARNING_RATE,
    SUBSAMPLE,
    COLSAMPLE_BYTREE,
)

logger = logging.getLogger(__name__)


# ======================================================
# TRAIN / TEST SPLIT
# ======================================================

def split_data(X, y):

    split_index = int(len(X) * (1 - TEST_SIZE))

    X_train = X.iloc[:split_index].copy()
    X_test = X.iloc[split_index:].copy()

    y_train = y.iloc[:split_index].copy()
    y_test = y.iloc[split_index:].copy()

    return X_train, X_test, y_train, y_test


# ======================================================
# CREATE MODEL
# ======================================================

def create_model():

    model = XGBRegressor(

        objective="reg:squarederror",

        random_state=RANDOM_STATE,

        n_estimators=N_ESTIMATORS,

        learning_rate=LEARNING_RATE,

        max_depth=MAX_DEPTH,

        subsample=SUBSAMPLE,

        colsample_bytree=COLSAMPLE_BYTREE,

        tree_method="hist",

        n_jobs=-1,

        verbosity=0,

    )

    return model


# ======================================================
# TRAIN
# ======================================================

def train_models(X, y_dict):

    logger.info("Scaling Features...")

    scaler = StandardScaler()

    split_index = int(len(X) * (1 - TEST_SIZE))

    X_train = X.iloc[:split_index]
    X_test = X.iloc[split_index:]

    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    models = {}

    metrics = {}

    for target in ["open", "high", "low", "close"]:

        logger.info(f"Training {target.upper()} Model")

        y_train = y_dict[target].iloc[:split_index]
        y_test = y_dict[target].iloc[split_index:]

        model = create_model()

        model.fit(
            X_train_scaled,
            y_train,
            eval_set=[(X_test_scaled, y_test)],
            verbose=False,
        )

        prediction = model.predict(X_test_scaled)

        mae = mean_absolute_error(y_test, prediction)

        rmse = np.sqrt(mean_squared_error(y_test, prediction))

        r2 = r2_score(y_test, prediction)

        logger.info(
            f"{target.upper()} -> "
            f"MAE={mae:.4f} "
            f"RMSE={rmse:.4f} "
            f"R2={r2:.4f}"
        )

        models[target] = model

        metrics[target] = {

            "MAE": mae,

            "RMSE": rmse,

            "R2": r2

        }

    return models, scaler, metrics


# ======================================================
# SAVE
# ======================================================

def save_models(

    models,

    scaler,

    feature_columns,

):

    os.makedirs(MODEL_DIR, exist_ok=True)

    for target in models:

        joblib.dump(

            models[target],

            os.path.join(

                MODEL_DIR,

                f"{target}_model.pkl"

            )

        )

    joblib.dump(

        scaler,

        os.path.join(

            MODEL_DIR,

            "scaler.pkl"

        )

    )

    joblib.dump(

        feature_columns,

        os.path.join(

            MODEL_DIR,

            "features.pkl"

        )

    )

    metadata = {

        "model": "XGBoost",

        "targets": list(models.keys()),

        "features": len(feature_columns),

    }

    joblib.dump(

        metadata,

        os.path.join(

            MODEL_DIR,

            "metadata.pkl"

        )

    )

    logger.info("Models Saved Successfully")


# ======================================================
# LOAD
# ======================================================

def load_models():

    models = {}

    for target in [

        "open",

        "high",

        "low",

        "close",

    ]:

        models[target] = joblib.load(

            os.path.join(

                MODEL_DIR,

                f"{target}_model.pkl"

            )

        )

    scaler = joblib.load(

        os.path.join(

            MODEL_DIR,

            "scaler.pkl"

        )

    )

    features = joblib.load(

        os.path.join(

            MODEL_DIR,

            "features.pkl"

        )

    )

    metadata = joblib.load(

        os.path.join(

            MODEL_DIR,

            "metadata.pkl"

        )

    )

    logger.info("Models Loaded Successfully")

    return {

        "models": models,

        "scaler": scaler,

        "features": features,

        "metadata": metadata,

    }


# ======================================================
# PREDICT
# ======================================================

def predict(models, scaler, feature_columns, latest_df):

    latest = latest_df[feature_columns]

    latest_scaled = scaler.transform(latest)

    prediction = {

        "Open": float(
            models["open"].predict(latest_scaled)[0]
        ),

        "High": float(
            models["high"].predict(latest_scaled)[0]
        ),

        "Low": float(
            models["low"].predict(latest_scaled)[0]
        ),

        "Close": float(
            models["close"].predict(latest_scaled)[0]
        ),

    }

    # Validate OHLC

    prediction["High"] = max(
        prediction["Open"],
        prediction["High"],
        prediction["Low"],
        prediction["Close"],
    )

    prediction["Low"] = min(
        prediction["Open"],
        prediction["High"],
        prediction["Low"],
        prediction["Close"],
    )

    return prediction


# ======================================================
# FEATURE IMPORTANCE
# ======================================================

def feature_importance(model, feature_columns):

    importance = pd.DataFrame({

        "Feature": feature_columns,

        "Importance": model.feature_importances_

    })

    importance = importance.sort_values(

        "Importance",

        ascending=False

    )

    return importance
