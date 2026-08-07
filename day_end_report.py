````python
"""
day_end_report.py

Compare predicted OHLC prices with actual market OHLC prices.

Telegram report:
    Predicted | Actual | Difference | Difference %

Excel report:
    Full detailed OHLC comparison
"""

import os
import logging

import pandas as pd
import requests
import yfinance as yf

from config import (
    REPORT_DIR,
    BOT_TOKEN,
    CHAT_ID,
)


# ======================================================
# LOGGING
# ======================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# ======================================================
# FILES
# ======================================================

HISTORY_FILE = os.path.join(
    REPORT_DIR,
    "prediction_history.csv"
)


# ======================================================
# GET ACTUAL OHLC
# ======================================================

def get_actual_ohlc(symbol, prediction_date):

    ticker = f"{symbol}.NS"

    try:

        logger.info(
            f"Downloading actual data: {ticker}"
        )

        df = yf.download(
            ticker,
            period="5d",
            auto_adjust=False,
            progress=False,
            threads=False
        )

        if df.empty:

            logger.warning(
                f"No actual data available for {symbol}"
            )

            return None


        # ------------------------------------------
        # Handle MultiIndex
        # ------------------------------------------

        if isinstance(
            df.columns,
            pd.MultiIndex
        ):

            df.columns = (
                df.columns
                .get_level_values(0)
            )


        # ------------------------------------------
        # Reset index
        # ------------------------------------------

        df = df.reset_index()


        # ------------------------------------------
        # Convert Date
        # ------------------------------------------

        df["Date"] = pd.to_datetime(
            df["Date"]
        ).dt.strftime(
            "%Y-%m-%d"
        )


        # ------------------------------------------
        # Find prediction date
        # ------------------------------------------

        row = df[
            df["Date"] == prediction_date
        ]


        # ------------------------------------------
        # If unavailable, use first trading day
        # after prediction date.
        # ------------------------------------------

        if row.empty:

            future_rows = df[
                df["Date"] > prediction_date
            ]

            if future_rows.empty:

                logger.warning(
                    f"Actual price not available for "
                    f"{symbol} after {prediction_date}"
                )

                return None

            row = future_rows.iloc[[0]]


        row = row.iloc[0]


        return {

            "Actual_Date":
                row["Date"],

            "Actual_Open":
                float(row["Open"]),

            "Actual_High":
                float(row["High"]),

            "Actual_Low":
                float(row["Low"]),

            "Actual_Close":
                float(row["Close"]),

        }


    except Exception as e:

        logger.warning(
            f"{symbol}: Actual data error: {e}"
        )

        return None


# ======================================================
# PERCENTAGE DIFFERENCE
# ======================================================

def percentage_difference(
    predicted,
    actual
):

    if predicted == 0:

        return 0.0

    return (
        (actual - predicted)
        / predicted
    ) * 100


# ======================================================
# CREATE DAY END REPORT
# ======================================================

def create_day_end_report(
    prediction_date=None
):

    if not os.path.exists(
        HISTORY_FILE
    ):

        logger.error(
            "Prediction history file not found."
        )

        return None


    try:

        history = pd.read_csv(
            HISTORY_FILE
        )


        if history.empty:

            logger.error(
                "Prediction history is empty."
            )

            return None


        # ------------------------------------------
        # Latest prediction date
        # ------------------------------------------

        if prediction_date is None:

            prediction_date = (
                history[
                    "Prediction_Date"
                ]
                .astype(str)
                .max()
            )


        logger.info(
            f"Creating day-end report for "
            f"{prediction_date}"
        )


        # ------------------------------------------
        # Get predictions
        # ------------------------------------------

        predictions = history[
            history[
                "Prediction_Date"
            ].astype(str)
            == str(prediction_date)
        ].copy()


        if predictions.empty:

            logger.error(
                f"No predictions found for "
                f"{prediction_date}"
            )

            return None


        predictions = (
            predictions
            .drop_duplicates(
                subset=["Stock"],
                keep="last"
            )
        )


        report_rows = []


        # ==========================================
        # PROCESS STOCKS
        # ==========================================

        for _, prediction in predictions.iterrows():

            symbol = str(
                prediction["Stock"]
            ).strip()


            actual = get_actual_ohlc(
                symbol,
                str(prediction_date)
            )


            if actual is None:

                logger.warning(
                    f"Skipping {symbol}"
                )

                continue


            # --------------------------------------
            # Predicted
            # --------------------------------------

            predicted_open = float(
                prediction["Open"]
            )

            predicted_high = float(
                prediction["High"]
            )

            predicted_low = float(
                prediction["Low"]
            )

            predicted_close = float(
                prediction["Close"]
            )


            # --------------------------------------
            # Actual
            # --------------------------------------

            actual_open = actual[
                "Actual_Open"
            ]

            actual_high = actual[
                "Actual_High"
            ]

            actual_low = actual[
                "Actual_Low"
            ]

            actual_close = actual[
                "Actual_Close"
            ]


            # --------------------------------------
            # Difference
            # --------------------------------------

            open_diff = (
                actual_open
                - predicted_open
            )

            high_diff = (
                actual_high
                - predicted_high
            )

            low_diff = (
                actual_low
                - predicted_low
            )

            close_diff = (
                actual_close
                - predicted_close
            )


            # --------------------------------------
            # Difference %
            # --------------------------------------

            open_pct = percentage_difference(
                predicted_open,
                actual_open
            )

            high_pct = percentage_difference(
                predicted_high,
                actual_high
            )

            low_pct = percentage_difference(
                predicted_low,
                actual_low
            )

            close_pct = percentage_difference(
                predicted_close,
                actual_close
            )


            report_rows.append({

                "Prediction_Date":
                    prediction_date,

                "Actual_Date":
                    actual["Actual_Date"],

                "Stock":
                    symbol,


                "Predicted_Open":
                    round(predicted_open, 2),

                "Actual_Open":
                    round(actual_open, 2),

                "Open_Difference":
                    round(open_diff, 2),

                "Open_Difference_%":
                    round(open_pct, 2),


                "Predicted_High":
                    round(predicted_high, 2),

                "Actual_High":
                    round(actual_high, 2),

                "High_Difference":
                    round(high_diff, 2),

                "High_Difference_%":
                    round(high_pct, 2),


                "Predicted_Low":
                    round(predicted_low, 2),

                "Actual_Low":
                    round(actual_low, 2),

                "Low_Difference":
                    round(low_diff, 2),

                "Low_Difference_%":
                    round(low_pct, 2),


                "Predicted_Close":
                    round(predicted_close, 2),

                "Actual_Close":
                    round(actual_close, 2),

                "Close_Difference":
                    round(close_diff, 2),

                "Close_Difference_%":
                    round(close_pct, 2),

            })


        # ==========================================
        # CREATE REPORT
        # ==========================================

        if not report_rows:

            logger.error(
                "No actual prices available."
            )

            return None


        report = pd.DataFrame(
            report_rows
        )


        # ==========================================
        # SAVE EXCEL
        # ==========================================

        os.makedirs(
            REPORT_DIR,
            exist_ok=True
        )


        filename = os.path.join(
            REPORT_DIR,
            f"day_end_{prediction_date}.xlsx"
        )


        report.to_excel(
            filename,
            index=False
        )


        logger.info(
            f"Day-end Excel saved: {filename}"
        )


        return report, filename


    except Exception as e:

        logger.exception(
            f"Day-end report failed: {e}"
        )

        return None


# ======================================================
# SEND TELEGRAM REPORT
# ======================================================

def send_day_end_telegram(
    report,
    filename,
    prediction_date
):

    if report is None or report.empty:

        return False


    if not BOT_TOKEN or not CHAT_ID:

        logger.warning(
            "Telegram credentials missing."
        )

        return False


    # ==========================================
    # AVERAGE ERROR
    # ==========================================

    avg_open_error = (
        report[
            "Open_Difference_%"
        ].abs().mean()
    )

    avg_high_error = (
        report[
            "High_Difference_%"
        ].abs().mean()
    )

    avg_low_error = (
        report[
            "Low_Difference_%"
        ].abs().mean()
    )

    avg_close_error = (
        report[
            "Close_Difference_%"
        ].abs().mean()
    )


    # ==========================================
    # TELEGRAM MESSAGE
    # ==========================================

    message = (
        "📊 *AI NSE DAY-END REPORT*\n\n"

        f"📅 Date: `{prediction_date}`\n\n"

        f"📈 Stocks Evaluated: "
        f"{len(report)}\n\n"

        "🎯 *AVERAGE ABSOLUTE ERROR*\n\n"

        f"Open  : {avg_open_error:.2f}%\n"
        f"High  : {avg_high_error:.2f}%\n"
        f"Low   : {avg_low_error:.2f}%\n"
        f"Close : {avg_close_error:.2f}%\n\n"

        "📋 *PREDICTED vs ACTUAL*\n"
    )


    # ==========================================
    # STOCK TABLES
    # ==========================================

    for _, row in report.iterrows():

        message += (
            "\n"
            f"📌 *{row['Stock']}*\n"
            "```\n"
            f"{'':<8}"
            f"{'Predicted':>12}"
            f"{'Actual':>12}"
            f"{'Diff':>10}"
            f"{'Diff %':>10}\n"

            f"{'-' * 52}\n"

            f"{'Open':<8}"
            f"{row['Predicted_Open']:>12.2f}"
            f"{row['Actual_Open']:>12.2f}"
            f"{row['Open_Difference']:>+10.2f}"
            f"{row['Open_Difference_%']:>+10.2f}%\n"

            f"{'High':<8}"
            f"{row['Predicted_High']:>12.2f}"
            f"{row['Actual_High']:>12.2f}"
            f"{row['High_Difference']:>+10.2f}"
            f"{row['High_Difference_%']:>+10.2f}%\n"

            f"{'Low':<8}"
            f"{row['Predicted_Low']:>12.2f}"
            f"{row['Actual_Low']:>12.2f}"
            f"{row['Low_Difference']:>+10.2f}"
            f"{row['Low_Difference_%']:>+10.2f}%\n"

            f"{'Close':<8}"
            f"{row['Predicted_Close']:>12.2f}"
            f"{row['Actual_Close']:>12.2f}"
            f"{row['Close_Difference']:>+10.2f}"
            f"{row['Close_Difference_%']:>+10.2f}%\n"

            "```\n"
        )


    # ==========================================
    # SEND TELEGRAM MESSAGE
    # ==========================================

    send_message_url = (
        f"https://api.telegram.org/"
        f"bot{BOT_TOKEN}/sendMessage"
    )


    try:

        response = requests.post(
            send_message_url,
            data={
                "chat_id": CHAT_ID,
                "text": message,
                "parse_mode": "Markdown"
            },
            timeout=30
        )


        if response.status_code != 200:

            logger.error(
                response.text
            )

            return False


        logger.info(
            "Day-end Telegram message sent."
        )


        # ======================================
        # SEND EXCEL FILE
        # ======================================

        document_url = (
            f"https://api.telegram.org/"
            f"bot{BOT_TOKEN}/sendDocument"
        )


        with open(
            filename,
            "rb"
        ) as file:

            response = requests.post(
                document_url,
                data={
                    "chat_id": CHAT_ID
                },
                files={
                    "document": file
                },
                timeout=60
            )


        if response.status_code == 200:

            logger.info(
                "Day-end Excel sent to Telegram."
            )

            return True


        logger.error(
            response.text
        )

        return False


    except Exception as e:

        logger.exception(
            f"Telegram error: {e}"
        )

        return False


# ======================================================
# MAIN
# ======================================================

def main():

    try:

        result = create_day_end_report()


        if result is None:

            logger.error(
                "Could not create day-end report."
            )

            return False


        report, filename = result


        prediction_date = (
            report[
                "Prediction_Date"
            ].iloc[0]
        )


        success = send_day_end_telegram(
            report,
            filename,
            prediction_date
        )


        if success:

            logger.info(
                "Day-end process completed successfully."
            )

        else:

            logger.warning(
                "Report created but Telegram "
                "delivery failed."
            )


        return True


    except Exception as e:

        logger.exception(
            f"Day-end process failed: {e}"
        )

        return False


# ======================================================
# ENTRY POINT
# ======================================================

if __name__ == "__main__":

    success = main()

    if success:

        logger.info(
            "Day-end report completed."
        )

    else:

        logger.error(
            "Day-end report failed."
        )
````
