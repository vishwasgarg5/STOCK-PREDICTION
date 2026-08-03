"""
telegram_bot.py
Send prediction results to Telegram
"""

import logging
import requests

from config import BOT_TOKEN, CHAT_ID

logger = logging.getLogger(__name__)


def send_predictions(predictions, prediction_date):

    if not predictions:

        logger.warning("No predictions to send.")

        return

    message = (
        "📈 AI NSE STOCK PREDICTION\n\n"
        f"Prediction Date : {prediction_date}\n\n"
    )

    for stock in predictions:

        message += (
            f"🏷 {stock['Stock']}\n"
            f"Open  : {stock['Open']}\n"
            f"High  : {stock['High']}\n"
            f"Low   : {stock['Low']}\n"
            f"Close : {stock['Close']}\n\n"
        )

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message,
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

            logger.error(
                f"Telegram Error {response.status_code}"
            )

            logger.error(response.text)

    except Exception as e:

        logger.exception(e)
