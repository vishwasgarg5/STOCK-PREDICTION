"""
telegram_bot.py
Send AI NSE Stock Prediction to Telegram
"""

import os
import logging
import requests

from config import BOT_TOKEN, CHAT_ID, REPORT_DIR

logger = logging.getLogger(__name__)


# ==========================================
# SEND PREDICTIONS
# ==========================================

def send_predictions(predictions, prediction_date):

    if not predictions:

        logger.warning("No predictions to send.")

        return

    # -----------------------------
    # Create Table
    # -----------------------------

    message = (
        "📈 *AI NSE STOCK PREDICTION*\n\n"
        f"📅 *Prediction Date:* `{prediction_date}`\n\n"
        "```\n"
        f"{'Stock':<12}{'Open':>10}{'High':>10}{'Low':>10}{'Close':>10}\n"
        + "-" * 52 + "\n"
    )

    for stock in predictions:

        message += (
            f"{stock['Stock']:<12}"
            f"{stock['Open']:>10.2f}"
            f"{stock['High']:>10.2f}"
            f"{stock['Low']:>10.2f}"
            f"{stock['Close']:>10.2f}\n"
        )

    message += "```"

    # -----------------------------
    # Send Message
    # -----------------------------

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:

        response = requests.post(
            url,
            data=payload,
            timeout=30
        )

        if response.status_code == 200:

            logger.info("Telegram message sent successfully.")

        else:

            logger.error(response.text)

    except Exception as e:

        logger.exception(e)

    # -----------------------------
    # Send Excel File
    # -----------------------------

    excel_file = os.path.join(
        REPORT_DIR,
        f"prediction_{prediction_date}.xlsx"
    )

    if os.path.exists(excel_file):

        try:

            url = (
                f"https://api.telegram.org/"
                f"bot{BOT_TOKEN}/sendDocument"
            )

            with open(excel_file, "rb") as f:

                requests.post(
                    url,
                    data={
                        "chat_id": CHAT_ID
                    },
                    files={
                        "document": f
                    },
                    timeout=60
                )

            logger.info("Excel report sent.")

        except Exception as e:

            logger.exception(e)
