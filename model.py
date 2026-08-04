"""
model.py
Train, Save and Load AI Models
"""

import os
import joblib
import logging
import numpy as np

from datetime import datetime
import pandas as pd

from config import MODEL_HISTORY_FILE

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    mean_absolute_percentage_error,
    r2_score,
)

from xgboost import XGBRegressor

from config import (
    MODEL_DIR,
    RANDOM_STATE,
    N_ESTIMATORS,
    MAX_DEPTH,
    LEARNING_RATE,
    SUBSAMPLE,
    COLSAMPLE_BYTREE,
)

logger = logging.getLogger(__name__)


# ==========================================
# CREATE MODEL
# ==========================================

def build_model():

    return XGBRegressor(

        objective="reg:squarederror",

        random_state=RANDOM_STATE,

        n_estimators=N_ESTIMATORS,

        max_depth=MAX_DEPTH,

        learning_rate=LEARNING_RATE,

        subsample=SUBSAMPLE,

        colsample_bytree=COLSAMPLE_BYTREE,

        n_jobs=-1,

    )


# ==========================================
# TRAIN
# ==========================================

def train_models(X, y):

    scaler = StandardScaler()

    X_scaled = scaler.fit_transform(X)
    
    # Create time-series validation split
    tscv = TimeSeriesSplit(n_splits=5)
    
    # Keep only the last split
    for train_index, test_index in tscv.split(X_scaled):
        pass
    
    models = {}

    for target in ["open", "high", "low", "close"]:

        logger.info(f"Training {target.upper()} model...")
    
        model = build_model()
    
        # Train using historical data
        model.fit(
            X_scaled[train_index],
            y[target].iloc[train_index]
        )
    
        # Evaluate on unseen recent data
        metrics = evaluate_model(
            model,
            X_scaled[test_index],
            y[target].iloc[test_index]
        )
    
        logger.info(
            f"{target.upper()} Metrics | "
            f"MAE: {metrics['MAE']:.2f} | "
            f"RMSE: {metrics['RMSE']:.2f} | "
            f"MAPE: {metrics['MAPE']:.2f}% | "
            f"R2: {metrics['R2']:.4f}"
        )
    
        # Retrain final model on all available data
        model.fit(
            X_scaled,
            y[target]
        )
    
        models[target] = model

    return models, scaler


# ==========================================
# SAVE
# ==========================================

def save_models(
    models,
    scaler,
    feature_columns
):

    os.makedirs(
        MODEL_DIR,
        exist_ok=True
    )

    joblib.dump(
        models["open"],
        os.path.join(
            MODEL_DIR,
            "open_model.pkl"
        )
    )

    joblib.dump(
        models["high"],
        os.path.join(
            MODEL_DIR,
            "high_model.pkl"
        )
    )

    joblib.dump(
        models["low"],
        os.path.join(
            MODEL_DIR,
            "low_model.pkl"
        )
    )

    joblib.dump(
        models["close"],
        os.path.join(
            MODEL_DIR,
            "close_model.pkl"
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

    logger.info("Models Saved Successfully")


# ==========================================
# LOAD
# ==========================================

def load_models():

    models = {

        "open": joblib.load(
            os.path.join(
                MODEL_DIR,
                "open_model.pkl"
            )
        ),

        "high": joblib.load(
            os.path.join(
                MODEL_DIR,
                "high_model.pkl"
            )
        ),

        "low": joblib.load(
            os.path.join(
                MODEL_DIR,
                "low_model.pkl"
            )
        ),

        "close": joblib.load(
            os.path.join(
                MODEL_DIR,
                "close_model.pkl"
            )
        ),

    }

    scaler = joblib.load(
        os.path.join(
            MODEL_DIR,
            "scaler.pkl"
        )
    )

    feature_columns = joblib.load(
        os.path.join(
            MODEL_DIR,
            "features.pkl"
        )
    )

    logger.info("Models Loaded Successfully")

    return {

        "models": models,

        "scaler": scaler,

        "features": feature_columns,

    }

# ==========================================
# EVALUATE MODEL
# ==========================================

def evaluate_model(model, X_test, y_test):

    predictions = model.predict(X_test)

    metrics = {

        "MAE": float(
            mean_absolute_error(
                y_test,
                predictions
            )
        ),

        "RMSE": float(
            np.sqrt(
                mean_squared_error(
                    y_test,
                    predictions
                )
            )
        ),

        "MAPE": float(
            mean_absolute_percentage_error(
                y_test,
                predictions
            ) * 100
        ),

        "R2": float(
            r2_score(
                y_test,
                predictions
            )
        )

    }

    return metrics

# ==========================================
# SAVE MODEL METRICS HISTORY
# ==========================================

def save_model_history(model_name, metrics):

    record = {

        "Date": datetime.now().strftime("%Y-%m-%d"),

        "Model": model_name.upper(),

        "MAE": metrics["MAE"],

        "RMSE": metrics["RMSE"],

        "MAPE": metrics["MAPE"],

        "R2": metrics["R2"]

    }

    df = pd.DataFrame([record])


    if os.path.exists(MODEL_HISTORY_FILE):

        old = pd.read_csv(
            MODEL_HISTORY_FILE
        )

        df = pd.concat(
            [old, df],
            ignore_index=True
        )


    df.to_csv(
        MODEL_HISTORY_FILE,
        index=False
    )
