"""
model.py
Train, Save and Load XGBoost Models
"""

import os
import joblib
import logging

from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
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


# =====================================
# SPLIT DATA
# =====================================

def split_data(X, y):

    split = int(len(X) * (1 - TEST_SIZE))

    X_train = X.iloc[:split]
    X_test = X.iloc[split:]

    y_train = y.iloc[:split]
    y_test = y.iloc[split:]

    return X_train, X_test, y_train, y_test


# =====================================
# CREATE MODEL
# =====================================

def create_model():

    return XGBRegressor(

        objective="reg:squarederror",

        random_state=RANDOM_STATE,

        n_estimators=N_ESTIMATORS,

        max_depth=MAX_DEPTH,

        learning_rate=LEARNING_RATE,

        subsample=SUBSAMPLE,

        colsample_bytree=COLSAMPLE_BYTREE,

        n_jobs=-1
    )


# =====================================
# TRAIN ALL MODELS
# =====================================

def train_models(X, y_dict):

    scaler = StandardScaler()

    X_scaled = scaler.fit_transform(X)

    models = {}

    for target in ["open", "high", "low", "close"]:

        logger.info(f"Training {target.upper()} model...")

        model = create_model()

        model.fit(

            X_scaled,

            y_dict[target]

        )

        models[target] = model

    models["scaler"] = scaler

    return models


# =====================================
# EVALUATE
# =====================================

def evaluate_model(model, scaler, X, y):

    split = int(len(X) * (1 - TEST_SIZE))

    X_train = X.iloc[:split]

    X_test = X.iloc[split:]

    y_train = y.iloc[:split]

    y_test = y.iloc[split:]

    scaler.fit(X_train)

    X_test_scaled = scaler.transform(X_test)

    prediction = model.predict(X_test_scaled)

    mae = mean_absolute_error(

        y_test,

        prediction

    )

    rmse = mean_squared_error(

        y_test,

        prediction,

        squared=False

    )

    r2 = r2_score(

        y_test,

        prediction

    )

    logger.info(f"MAE  : {mae:.2f}")

    logger.info(f"RMSE : {rmse:.2f}")

    logger.info(f"R²   : {r2:.4f}")


# =====================================
# SAVE
# =====================================

def save_models(models, feature_columns):

    for name in ["open", "high", "low", "close"]:

        joblib.dump(

            models[name],

            os.path.join(

                MODEL_DIR,

                f"{name}_model.pkl"

            )

        )

    joblib.dump(

        models["scaler"],

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

    logger.info("Models saved successfully")


# =====================================
# LOAD
# =====================================

def load_models():

    models = {}

    for name in ["open", "high", "low", "close"]:

        models[name] = joblib.load(

            os.path.join(

                MODEL_DIR,

                f"{name}_model.pkl"

            )

        )

    models["scaler"] = joblib.load(

        os.path.join(

            MODEL_DIR,

            "scaler.pkl"

        )

    )

    models["features"] = joblib.load(

        os.path.join(

            MODEL_DIR,

            "features.pkl"

        )

    )

    logger.info("Models loaded successfully")

    return models
