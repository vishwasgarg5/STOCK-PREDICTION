"""
telegram_bot.py
Telegram Notification Module
"""

import logging
import requests
import pandas as pd

from config import BOT_TOKEN, CHAT_ID

logger = logging.getLogger(__name__)


# =====================================================
# FORMAT MESSAGE
# =====================================================

def format_message(predictions, prediction_date):

    if not predictions:
        return "❌ No stock predictions generated."

    df = pd.DataFrame(predictions)

    df = df.sort_values(
        by="Close",
        ascending=False
    )

    message = []

    message.append("📈 AI NSE STOCK PREDICTION")
    message.append("")
    message.append(f"📅 Prediction Date : {prediction_date}")
    message.append("")
    message.append(
        "{:<12}{:>10}{:>10}{:>10}{:>10}".format(
            "Stock",
            "Open",
            "High",
            "Low",
            "Close",
        )
    )

    message.append("-" * 55)

    for _, row in df.iterrows():

        message.append(
            "{:<12}{:>10.2f}{:>10.2f}{:>10.2f}{:>10.2f}".format(
                row["Stock"],
                row["Open"],
                row["High"],
                row["Low"],
                row["Close"],
            )
        )

    return "```" + "\n".join(message) + "```"


# =====================================================
# SEND TELEGRAM
# =====================================================

def send_message(message):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {

        "chat_id": CHAT_ID,

        "text": message,

        "parse_mode": "Markdown"

    }

    try:

        response = requests.post(

            url,

            json=payload,

            timeout=20

        )

        response.raise_for_status()

        logger.info("Telegram Message Sent")

        return True

    except Exception as e:

        logger.error(f"Telegram Error : {e}")

        return False


# =====================================================
# SEND PREDICTIONS
# =====================================================

def send_predictions(predictions, prediction_date):

    message = format_message(

        predictions,

        prediction_date

    )

    return send_message(message)
