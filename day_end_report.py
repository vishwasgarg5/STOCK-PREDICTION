```python
"""
day_end_report.py

Compare predicted OHLC prices with actual market OHLC prices.

The report contains:

    Stock
    Predicted Open
    Actual Open
    Open Difference
    Open Difference %

    Predicted High
    Actual High
    High Difference
    High Difference %

    Predicted Low
    Actual Low
    Low Difference
    Low Difference %

    Predicted Close
    Actual Close
    Close Difference
    Close Difference %

The report is sent to Telegram after market close.
"""

import os
import logging
from datetime import datetime

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
# GET ACTUAL STOCK DATA
# ======================================================

def get_actual_ohlc(symbol, prediction_date):

    ticker = f"{symbol}.NS"

    try:

        logger.info(
            f"Downloading actual data: {ticker}"
        )

        # ------------------------------------------
        # Download fresh market data
        # ------------------------------------------

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
        # If prediction date is not available,
        # find the first trading day after it.
        # ------------------------------------------

        if row.empty:

            future_rows = df[
                df["Date"] > prediction_date
            ]

            if future_rows.empty:

                logger.warning(
                    f"Actual price not available for "
                    f"{symbol} on/after {prediction_date}"
                )

                return None

            row = future_rows.iloc[[0]]


        row = row.iloc[0]


        actual = {

            "Actual_Date": row["Date"],

            "Actual_Open": float(
                row["Open"]
            ),

            "Actual_High": float(
                row["High"]
            ),

            "Actual_Low": float(
                row["Low"]
            ),

            "Actual_Close": float(
                row["Close"]
            ),

        }


        return actual


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

    # ------------------------------------------
    # Check history file
    # ------------------------------------------

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
        # If no date supplied, use latest date
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
        # Select predictions
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


        # ------------------------------------------
        # Remove duplicate stocks
        # ------------------------------------------

        predictions = (
            predictions
            .drop_duplicates(
                subset=["Stock"],
                keep="last"
            )
        )


        report_rows = []


        # ==========================================
        # PROCESS EACH STOCK
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
            # Predicted values
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
            # Actual values
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
            # Differences
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
            # Percentage differences
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


            # --------------------------------------
            # Store row
            # --------------------------------------

            report_rows.append({

                "Prediction_Date":
                    prediction_date,

                "Actual_Date":
                    actual["Actual_Date"],

                "Stock":
                    symbol,

                "Predicted_Open":
                    round(
                        predicted_open,
                        2
                    ),

                "Actual_Open":
                    round(
                        actual_open,
                        2
                    ),

                "Open_Difference":
                    round(
                        open_diff,
                        2
                    ),

                "Open_Difference_%":
                    round(
                        open_pct,
                        2
                    ),


                "Predicted_High":
                    round(
                        predicted_high,
                        2
                    ),

                "Actual_High":
                    round(
                        actual_high,
                        2
                    ),

                "High_Difference":
                    round(
                        high_diff,
                        2
                    ),

                "High_Difference_%":
                    round(
                        high_pct,
                        2
                    ),


                "Predicted_Low":
                    round(
                        predicted_low,
                        2
                    ),

                "Actual_Low":
                    round(
                        actual_low,
                        2
                    ),

                "Low_Difference":
                    round(
                        low_diff,
                        2
                    ),

                "Low_Difference_%":
                    round(
                        low_pct,
                        2
                    ),


                "Predicted_Close":
                    round(
                        predicted_close,
                        2
                    ),

                "Actual_Close":
                    round(
                        actual_close,
                        2
                    ),

                "Close_Difference":
                    round(
                        close_diff,
                        2
                    ),

                "Close_Difference_%":
                    round(
                        close_pct,
                        2
                    ),

            })


        # ==========================================
        # CREATE DATAFRAME
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
            "Telegram BOT_TOKEN or CHAT_ID missing."
        )

        return False


    # ==========================================
    # CALCULATE SUMMARY
    # ==========================================

    close_errors = (
        report[
            "Close_Difference_%"
        ].abs()
    )

    open_errors = (
        report[
            "Open_Difference_%"
        ].abs()
    )

    high_errors = (
        report[
            "High_Difference_%"
        ].abs()
    )

    low_errors = (
        report[
            "Low_Difference_%"
        ].abs()
    )


    avg_open_error = (
        open_errors.mean()
    )

    avg_high_error = (
        high_errors.mean()
    )

    avg_low_error = (
        low_errors.mean()
    )

    avg_close_error = (
        close_errors.mean()
    )


    # ==========================================
    # BUILD MESSAGE
    # ==========================================

    message = (
        "📊 *AI NSE DAY-END REPORT*\n\n"
        f"📅 Date: `{prediction_date}`\n\n"
        f"📈 Stocks Evaluated: "
        f"{len(report)}\n\n"

        "🎯 *Average Absolute Error*\n"
        f"Open  : {avg_open_error:.2f}%\n"
        f"High  : {avg_high_error:.2f}%\n"
        f"Low   : {avg_low_error:.2f}%\n"
        f"Close : {avg_close_error:.2f}%\n\n"

        "📋 *STOCK RESULTS*\n"
    )


    # ==========================================
    # STOCK RESULTS
    # ==========================================

    for _, row in report.iterrows():

        close_pct = (
            row["Close_Difference_%"]
        )

        open_pct = (
            row["Open_Difference_%"]
        )

        high_pct = (
            row["High_Difference_%"]
        )

        low_pct = (
            row["Low_Difference_%"]
        )


        message += (
            f"\n*{row['Stock']}*\n"
            f"Open  : "
            f"{row['Predicted_Open']:.2f}"
            f" → "
            f"{row['Actual_Open']:.2f}"
            f" ({open_pct:+.2f}%)\n"

            f"High  : "
            f"{row['Predicted_High']:.2f}"
            f" → "
            f"{row['Actual_High']:.2f}"
            f" ({high_pct:+.2f}%)\n"

            f"Low   : "
            f"{row['Predicted_Low']:.2f}"
            f" → "
            f"{row['Actual_Low']:.2f}"
            f" ({low_pct:+.2f}%)\n"

            f"Close : "
            f"{row['Predicted_Close']:.2f}"
            f" → "
            f"{row['Actual_Close']:.2f}"
            f" ({close_pct:+.2f}%)\n"
        )


    # ==========================================
    # SEND TEXT
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
        # SEND EXCEL
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
            ]
            .iloc[0]
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
                "Day-end report created but Telegram "
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
```
