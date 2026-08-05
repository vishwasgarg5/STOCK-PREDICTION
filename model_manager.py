"""
model_manager.py
Compare candidate model with existing model
"""

import json
import logging
import os
import shutil
from datetime import datetime

from config import MODEL_DIR, REPORT_DIR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


METADATA_FILE = os.path.join(
    MODEL_DIR,
    "metadata.json"
)

DEFAULT_MAE = float("inf")

def load_metadata():

    if not os.path.exists(METADATA_FILE):

        return None

    with open(METADATA_FILE, "r") as f:

        return json.load(f)

def get_production_mae(model_name):

    metadata = load_metadata()

    if metadata is None:
        return DEFAULT_MAE

    return metadata["mae"].get(
        model_name.lower(),
        DEFAULT_MAE
    )
        
def should_replace(model_name, candidate_mae):

    production_mae = get_production_mae(
        model_name
    )

    return candidate_mae < production_mae
    
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

    logger.info(f"Models backed up: {archive_dir}")

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

    logger.info("Production models replaced successfully.")

def update_metadata(mae_values):

    metadata = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "mae": mae_values
    }

    with open(METADATA_FILE, "w") as f:
        json.dump(
            metadata,
            f,
            indent=4
        )

    logger.info(f"Metadata updated: {METADATA_FILE}")
