"""
main.py
AI NSE Stock Prediction System
"""
import os
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

    # Create reports folder if it doesn't exist
    os.makedirs(REPORT_DIR, exist_ok=True)

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

    try:
        start = datetime.now()

        logger.info("=" * 60)
        logger.info("AI NSE STOCK PREDICTION")
        logger.info("=" * 60)
    
        # Download latest stock data
        logger.info("Downloading latest Nifty 500 data...")
        stock_data = get_all_stock_data()
    
        if not stock_data:
            logger.error("No stock data downloaded.")
            return False
    
        logger.info(f"Stocks downloaded: {len(stock_data)}")
    
        # Run screener
        logger.info("Running screener...")
        top_stocks = screen_stocks(stock_data)
    
        if not top_stocks:
            logger.error("No stocks selected by screener.")
            return False
    
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
        logger.info(f"Generated {len(predictions)} predictions")
    
        if not predictions:
            logger.error("No predictions generated.")
            return False
    
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
    
        logger.info("-" * 60)
        logger.info("FINAL PREDICTIONS")
        
        table = pd.DataFrame(predictions)
        
        logger.info("\n" + table.to_string(index=False))
    
        end = datetime.now()
    
        logger.info("-" * 60)
        logger.info("AI NSE STOCK PREDICTION SYSTEM")
        logger.info(f"Execution Time : {end - start}")
        logger.info("=" * 60)

        return True

    except Exception as e:

        logger.exception(f"Unexpected error: {e}")
        return False
    
# ======================================================
# ENTRY
# ======================================================

if __name__ == "__main__":

    success = main()

    if success:
        logger.info("Program completed successfully.")
    else:
        logger.error("Program terminated with errors.")
