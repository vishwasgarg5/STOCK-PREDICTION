"""
model_manager.py
Compare candidate model with existing model
"""

import json
import os
import pandas as pd
import shutil
from datetime import datetime

from config import MODEL_DIR

from config import REPORT_DIR


MODEL_HISTORY = os.path.join(
    REPORT_DIR,
    "model_history.csv"
)

METADATA_FILE = os.path.join(
    MODEL_DIR,
    "metadata.json"
)

def load_history():

    if not os.path.exists(MODEL_HISTORY):

        return None

    return pd.read_csv(
        MODEL_HISTORY
    )

def load_metadata():

    if not os.path.exists(METADATA_FILE):

        return None

    with open(METADATA_FILE, "r") as f:

        return json.load(f)
        
def get_previous_metrics(model_name):

    df = load_history()

    if df is None:
        return None

    df = df[
        df["Model"] == model_name.upper()
    ]

    # Need at least 2 records
    # because latest record is the new model

    if len(df) < 2:

        return None

    return df.iloc[-2]


def get_latest_metrics(model_name):

    df = load_history()

    if df is None:
        return None

    df = df[
        df["Model"] == model_name.upper()
    ]

    if df.empty:

        return None

    return df.iloc[-1]


def should_replace(model_name):

    old = get_previous_metrics(
        model_name
    )

    new = get_latest_metrics(
        model_name
    )


    if old is None or new is None:

        return False


    # Lower MAE is better

    if new["MAE"] < old["MAE"]:

        return True


    return False

def backup_current_models():

    archive_dir = os.path.join(
        MODEL_DIR,
        "archive",
        datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    )

    os.makedirs(
        archive_dir,
        exist_ok=True
    )


    for file in os.listdir(MODEL_DIR):

        source = os.path.join(
            MODEL_DIR,
            file
        )

        if os.path.isfile(source):

            shutil.copy(
                source,
                archive_dir
            )

    print(
        f"Models backed up: {archive_dir}"
    )


def replace_models(new_model_dir):

    backup_current_models()

    for file in os.listdir(new_model_dir):

        source = os.path.join(
            new_model_dir,
            file
        )
    
        destination = os.path.join(
            MODEL_DIR,
            file
        )
    
        # Skip copying same file
        if os.path.abspath(source) == os.path.abspath(destination):
            continue
    
        if os.path.isfile(source):
    
            shutil.copy(
                source,
                destination
            )

    print(
        "Production models replaced successfully."
    )
