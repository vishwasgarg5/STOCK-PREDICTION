"""
main.py
AI NSE Stock Prediction System
"""

import logging
from datetime import datetime
import pandas as pd

from data_loader import get_all_stock_data
from screener import screen_stocks
from predictor import predict_multiple
from telegram_bot import send_predictions
from config import REPORT_DIR

# ==========================================
# LOGGING
# ==========================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# ==========================================
# SAVE EXCEL
# ==========================================

def save_excel(predictions, prediction_date):

    if not predictions:
        return

    df = pd.DataFrame(predictions)

    filename = (
        f"{REPORT_DIR}/"
        f"prediction_{prediction_date}.xlsx"
    )

    df.to_excel(
        filename,
        index=False
    )

    logger.info(f"Excel Saved : {filename}")


# ==========================================
# MAIN
# ==========================================

def main():

    start = datetime.now()

    logger.info("Downloading Stock Data...")

    stock_data = get_all_stock_data()

    logger.info(
        f"Stocks Downloaded : {len(stock_data)}"
    )

    logger.info("Running Screener...")

    top_stocks = screen_stocks(stock_data)

    logger.info(top_stocks)

    top_stock_data = {

        symbol: stock_data[symbol]

        for symbol in top_stocks

    }

    logger.info("Predicting...")

    predictions = predict_multiple(
        top_stock_data
    )

    prediction_date = (
        datetime.now()
        .strftime("%Y-%m-%d")
    )

    save_excel(
        predictions,
        prediction_date
    )

    send_predictions(
        predictions,
        prediction_date
    )

    end = datetime.now()

    logger.info(
        f"Execution Time : {end-start}"
    )


# ==========================================
# ENTRY
# ==========================================

if __name__ == "__main__":

    main()
