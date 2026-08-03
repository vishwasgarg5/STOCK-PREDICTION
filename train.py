"""
train.py
Train AI models using all Nifty 500 stocks
"""

import logging
import pandas as pd

from data_loader import get_all_stock_data
from indicators import add_indicators
from feature_engineering import (
    create_features,
    create_targets,
    prepare_dataset,
)
from model import (
    train_models,
    save_models,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


def main():

    logger.info("Downloading Nifty 500 data...")

    stock_data = get_all_stock_data()

    logger.info(f"Stocks Loaded : {len(stock_data)}")

    training_frames = []

    for symbol, df in stock_data.items():

        try:

            df = add_indicators(df)

            df = create_features(df)

            df = create_targets(df)

            training_frames.append(df)

        except Exception as e:

            logger.warning(f"{symbol}: {e}")

    if not training_frames:

        raise ValueError("No training data generated.")

    logger.info("Combining all stock data...")

    combined_df = pd.concat(
        training_frames,
        ignore_index=True
    )

    logger.info(f"Training Rows : {len(combined_df)}")

    X, y, feature_columns, _ = prepare_dataset(
        combined_df
    )

    logger.info(f"Features : {len(feature_columns)}")

    models, scaler = train_models(X, y)

    save_models(
        models,
        scaler,
        feature_columns
    )

    logger.info("Training Completed Successfully")


if __name__ == "__main__":

    main()
