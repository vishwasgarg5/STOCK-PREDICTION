"""
main.py
AI NSE Stock Prediction System
"""

import logging
from datetime import datetime

import pandas as pd

from config import REPORT_DIR
from data_loader import get_all_stock_data
from screener import screen_stocks
from predictor import predict_multiple
from telegram_bot import send_predictions
from prediction_history import save_prediction_history


# ======================================================
# LOGGING
# ======================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# ======================================================
# SAVE REPORT
# ======================================================

def save_excel(predictions, prediction_date):

    if not predictions:
        logger.warning("No predictions to save.")
        return

    df = pd.DataFrame(predictions)

    filename = (
        f"{REPORT_DIR}/prediction_{prediction_date}.xlsx"
    )

    df.to_excel(
        filename,
        index=False
    )

    logger.info(f"Excel saved: {filename}")


# ======================================================
# MAIN
# ======================================================

def main():

    start = datetime.now()

    logger.info("=" * 60)
    logger.info("AI NSE STOCK PREDICTION")
    logger.info("=" * 60)

    # Download latest stock data
    logger.info("Downloading latest Nifty 500 data...")
    stock_data = get_all_stock_data()

    if not stock_data:
        logger.error("No stock data downloaded.")
        return

    logger.info(f"Stocks downloaded: {len(stock_data)}")

    # Run screener
    logger.info("Running screener...")
    top_stocks = screen_stocks(stock_data)

    if not top_stocks:
        logger.error("No stocks selected by screener.")
        return

    logger.info(f"Top Stocks: {top_stocks}")

    # Keep only screened stocks
    top_stock_data = {
        symbol: stock_data[symbol]
        for symbol in top_stocks
        if symbol in stock_data
    }

    # Prediction
    logger.info("Running prediction...")
    predictions = predict_multiple(top_stock_data)

    if not predictions:
        logger.error("No predictions generated.")
        return

    prediction_date = datetime.now().strftime("%Y-%m-%d")

    # Save report
    save_excel(
        predictions,
        prediction_date
    )

    # Save prediction history
    save_prediction_history(
        predictions,
        prediction_date
    )
    # Telegram
    send_predictions(
        predictions,
        prediction_date
    )

    logger.info("")
    logger.info("FINAL PREDICTIONS")

    for p in predictions:

        logger.info(
            f"{p['Stock']:12}"
            f" O:{p['Open']:8.2f}"
            f" H:{p['High']:8.2f}"
            f" L:{p['Low']:8.2f}"
            f" C:{p['Close']:8.2f}"
        )

    end = datetime.now()

    logger.info("")
    logger.info("=" * 60)
    logger.info(f"Execution Time : {end-start}")
    logger.info("=" * 60)


# ======================================================
# ENTRY
# ======================================================

if __name__ == "__main__":

    main()
