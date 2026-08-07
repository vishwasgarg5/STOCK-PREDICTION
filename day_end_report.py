"""
day_end_report.py

Compare AI predictions with actual market OHLC
after the NSE market closes.

Outputs:
    - Predicted vs Actual
    - Difference
    - Absolute Difference
    - Percentage Error
    - Accuracy
    - Excel report
    - CSV history
    - Telegram report
"""

import os
import time
import logging
from datetime import datetime

import pandas as pd
import yfinance as yf
import requests

from config import (
    REPORT_DIR,
    BOT_TOKEN,
    CHAT_ID
)

from prediction_history import (
    load_prediction_history
)


# ==========================================
# LOGGING
# ==========================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# ==========================================
# FILES
# ==========================================

DAY_END_HISTORY_FILE = os.path.join(
    REPORT_DIR,
    "day_end_history.csv"
)


# ==========================================
# DOWNLOAD ACTUAL DATA
# ==========================================

def get_actual_data(
    stocks,
    report_date
):
    """
    Download actual OHLC data for selected stocks.
    """

    actual_data = []

    for stock in stocks:

        symbol = (
            stock
            if stock.endswith(".NS")
            else f"{stock}.NS"
        )

        try:

            logger.info(
                f"Downloading actual data: {symbol}"
            )

            df = yf.download(
                symbol,
                start=report_date,
                end=(
                    pd.Timestamp(report_date)
                    + pd.Timedelta(days=1)
                ).strftime("%Y-%m-%d"),
                auto_adjust=False,
                progress=False,
                threads=False
            )

            if df.empty:

                logger.warning(
                    f"{symbol}: No actual data found."
                )

                continue

            # ----------------------------------
            # Handle MultiIndex
            # ----------------------------------

            if isinstance(
                df.columns,
                pd.MultiIndex
            ):

                df.columns = (
                    df.columns
                    .get_level_values(0)
                )

            required = [
                "Open",
                "High",
                "Low",
                "Close"
            ]

            missing = [
                col
                for col in required
                if col not in df.columns
            ]

            if missing:

                logger.warning(
                    f"{symbol}: Missing {missing}"
                )

                continue

            row = df.iloc[-1]

            actual_data.append(
                {
                    "Stock": stock.replace(
                        ".NS",
                        ""
                    ),

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
                    )
                }
            )

        except Exception as e:

            logger.warning(
                f"{symbol}: {e}"
            )

    return pd.DataFrame(
        actual_data
    )


# ==========================================
# CALCULATE ERROR
# ==========================================

def calculate_difference(
    predicted,
    actual
):
    """
    Calculate signed difference.

    Positive:
        Actual > Predicted

    Negative:
        Actual < Predicted
    """

    difference = actual - predicted

    absolute_difference = abs(
        difference
    )

    if actual != 0:

        percentage_error = (
            absolute_difference
            / abs(actual)
        ) * 100

    else:

        percentage_error = 0

    accuracy = max(
        0,
        100 - percentage_error
    )

    return (
        difference,
        absolute_difference,
        percentage_error,
        accuracy
    )


# ==========================================
# CREATE REPORT
# ==========================================

def create_day_end_report(
    predictions,
    actuals,
    report_date
):

    if predictions.empty:

        logger.error(
            "No predictions found."
        )

        return pd.DataFrame()

    if actuals.empty:

        logger.error(
            "No actual market data found."
        )

        return pd.DataFrame()

    # --------------------------------------
    # Merge predictions + actuals
    # --------------------------------------

    report = predictions.merge(
        actuals,
        on="Stock",
        how="inner"
    )

    if report.empty:

        logger.error(
            "No stocks could be matched."
        )

        return pd.DataFrame()

    # --------------------------------------
    # Calculate OHLC metrics
    # --------------------------------------

    for field in [
        "Open",
        "High",
        "Low",
        "Close"
    ]:

        results = report.apply(
            lambda row:
                calculate_difference(
                    row[field],
                    row[f"Actual_{field}"]
                ),
            axis=1
        )

        report[
            f"{field}_Difference"
        ] = results.apply(
            lambda x: x[0]
        )

        report[
            f"{field}_Absolute_Difference"
        ] = results.apply(
            lambda x: x[1]
        )

        report[
            f"{field}_Error_Percent"
        ] = results.apply(
            lambda x: x[2]
        )

        report[
            f"{field}_Accuracy"
        ] = results.apply(
            lambda x: x[3]
        )

    # --------------------------------------
    # Overall accuracy
    # --------------------------------------

    accuracy_columns = [
        "Open_Accuracy",
        "High_Accuracy",
        "Low_Accuracy",
        "Close_Accuracy"
    ]

    report[
        "Overall_Accuracy"
    ] = report[
        accuracy_columns
    ].mean(axis=1)

    # --------------------------------------
    # Add report date
    # --------------------------------------

    report.insert(
        0,
        "Report_Date",
        report_date
    )

    # --------------------------------------
    # Round numbers
    # --------------------------------------

    numeric_columns = report.select_dtypes(
        include="number"
    ).columns

    report[
        numeric_columns
    ] = report[
        numeric_columns
    ].round(2)

    return report


# ==========================================
# SAVE EXCEL
# ==========================================

def save_excel_report(
    report,
    report_date
):

    os.makedirs(
        REPORT_DIR,
        exist_ok=True
    )

    filename = os.path.join(
        REPORT_DIR,
        f"day_end_report_{report_date}.xlsx"
    )

    report.to_excel(
        filename,
        index=False
    )

    logger.info(
        f"Day-end Excel saved: {filename}"
    )

    return filename


# ==========================================
# SAVE HISTORY
# ==========================================

def save_day_end_history(
    report
):

    if report.empty:
        return

    os.makedirs(
        REPORT_DIR,
        exist_ok=True
    )

    if os.path.exists(
        DAY_END_HISTORY_FILE
    ):

        old = pd.read_csv(
            DAY_END_HISTORY_FILE
        )

        # Prevent duplicate report rows
        # for the same date + stock.

        if not old.empty:

            old = old[
                ~old.apply(
                    lambda row:
                        any(
                            (
                                str(row.get(
                                    "Report_Date",
                                    ""
                                ))
                                ==
                                str(
                                    report.iloc[0][
                                        "Report_Date"
                                    ]
                                )
                            )
                            and
                            (
                                str(row.get(
                                    "Stock",
                                    ""
                                ))
                                ==
                                str(stock)
                            )
                            for stock in report[
                                "Stock"
                            ].tolist()
                        ),
                    axis=1
                )
            ]

        report = pd.concat(
            [
                old,
                report
            ],
            ignore_index=True
        )

    report.to_csv(
        DAY_END_HISTORY_FILE,
        index=False
    )

    logger.info(
        f"Day-end history saved: "
        f"{DAY_END_HISTORY_FILE}"
    )


# ==========================================
# TELEGRAM MESSAGE
# ==========================================

def send_day_end_telegram(
    report,
    report_date
):

    if report.empty:

        logger.warning(
            "No day-end report to send."
        )

        return False

    if not BOT_TOKEN or not CHAT_ID:

        logger.error(
            "BOT_TOKEN or CHAT_ID missing."
        )

        return False

    # --------------------------------------
    # Overall system accuracy
    # --------------------------------------

    overall_accuracy = report[
        "Overall_Accuracy"
    ].mean()

    message = (
        "📊 *AI NSE DAY-END REPORT*\n\n"
        f"📅 *Date:* `{report_date}`\n\n"
        f"🎯 *Overall OHLC Accuracy:* "
        f"`{overall_accuracy:.2f}%`\n\n"
    )

    # --------------------------------------
    # Stock details
    # --------------------------------------

    for _, row in report.iterrows():

        stock = row["Stock"]

        message += (
            f"📌 *{stock}*\n\n"
        )

        for field in [
            "Open",
            "High",
            "Low",
            "Close"
        ]:

            predicted = row[field]

            actual = row[
                f"Actual_{field}"
            ]

            difference = row[
                f"{field}_Difference"
            ]

            error = row[
                f"{field}_Error_Percent"
            ]

            accuracy = row[
                f"{field}_Accuracy"
            ]

            message += (
                f"*{field}*\n"
                f"Predicted: ₹{predicted:.2f}\n"
                f"Actual:    ₹{actual:.2f}\n"
                f"Difference: ₹{difference:+.2f}\n"
                f"Error: {error:.2f}%\n"
                f"Accuracy: {accuracy:.2f}%\n\n"
            )

        message += (
            f"🎯 Stock Accuracy: "
            f"{row['Overall_Accuracy']:.2f}%\n\n"
            "--------------------\n\n"
        )

    # --------------------------------------
    # Telegram API
    # --------------------------------------

    url = (
        f"https://api.telegram.org/"
        f"bot{BOT_TOKEN}/sendMessage"
    )

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

            logger.info(
                "Day-end Telegram message sent."
            )

            return True

        logger.error(
            response.text
        )

        return False

    except Exception as e:

        logger.exception(e)

        return False


# ==========================================
# SEND EXCEL TO TELEGRAM
# ==========================================

def send_excel_to_telegram(
    excel_file
):

    if not BOT_TOKEN or not CHAT_ID:
        return False

    if not os.path.exists(
        excel_file
    ):
        return False

    url = (
        f"https://api.telegram.org/"
        f"bot{BOT_TOKEN}/sendDocument"
    )

    try:

        with open(
            excel_file,
            "rb"
        ) as file:

            response = requests.post(
                url,
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
                "Day-end Excel report sent."
            )

            return True

        logger.error(
            response.text
        )

        return False

    except Exception as e:

        logger.exception(e)

        return False


# ==========================================
# MAIN
# ==========================================

def main():

    try:

        logger.info("=" * 60)
        logger.info(
            "AI NSE DAY-END ACTUAL VS PREDICTED"
        )
        logger.info("=" * 60)

        # ----------------------------------
        # Load prediction history
        # ----------------------------------

        history = load_prediction_history()

        if history.empty:

            logger.error(
                "Prediction history is empty."
            )

            return False

        # ----------------------------------
        # Get latest prediction date
        # ----------------------------------

        history[
            "Prediction_Date"
        ] = pd.to_datetime(
            history["Prediction_Date"]
        )

        latest_prediction_date = (
            history[
                "Prediction_Date"
            ].max()
        )

        report_date = (
            latest_prediction_date
            .strftime("%Y-%m-%d")
        )

        logger.info(
            f"Checking predictions for: "
            f"{report_date}"
        )

        # ----------------------------------
        # Get latest predictions
        # ----------------------------------

        predictions = history[
            history[
                "Prediction_Date"
            ].dt.strftime("%Y-%m-%d")
            == report_date
        ].copy()

        if predictions.empty:

            logger.error(
                "No predictions for report date."
            )

            return False

        # ----------------------------------
        # Stock list
        # ----------------------------------

        stocks = predictions[
            "Stock"
        ].astype(str).tolist()

        logger.info(
            f"Stocks to compare: {stocks}"
        )

        # ----------------------------------
        # Download actual market data
        # ----------------------------------

        actuals = pd.DataFrame()

        # Try several times because Yahoo
        # Finance data can be delayed after
        # market close.

        for attempt in range(1, 4):

            logger.info(
                f"Downloading actual data "
                f"(attempt {attempt}/3)..."
            )

            actuals = get_actual_data(
                stocks,
                report_date
            )

            if len(actuals) == len(
                stocks
            ):

                break

            if attempt < 3:

                logger.info(
                    "Some actual data missing. "
                    "Waiting 60 seconds..."
                )

                time.sleep(60)

        # ----------------------------------
        # Validate
        # ----------------------------------

        if actuals.empty:

            logger.error(
                "Actual market data unavailable."
            )

            return False

        logger.info(
            f"Actual data received for "
            f"{len(actuals)} stocks."
        )

        # ----------------------------------
        # Create report
        # ----------------------------------

        report = create_day_end_report(
            predictions,
            actuals,
            report_date
        )

        if report.empty:

            logger.error(
                "Day-end report could not "
                "be generated."
            )

            return False

        # ----------------------------------
        # Save Excel
        # ----------------------------------

        excel_file = save_excel_report(
            report,
            report_date
        )

        # ----------------------------------
        # Save cumulative history
        # ----------------------------------

        save_day_end_history(
            report
        )

        # ----------------------------------
        # Send Telegram
        # ----------------------------------

        send_day_end_telegram(
            report,
            report_date
        )

        send_excel_to_telegram(
            excel_file
        )

        # ----------------------------------
        # Console output
        # ----------------------------------

        logger.info("-" * 60)
        logger.info(
            "DAY-END RESULTS"
        )
        logger.info("-" * 60)

        display_columns = [
            "Stock",
            "Open",
            "Actual_Open",
            "Open_Error_Percent",
            "High",
            "Actual_High",
            "High_Error_Percent",
            "Low",
            "Actual_Low",
            "Low_Error_Percent",
            "Close",
            "Actual_Close",
            "Close_Error_Percent",
            "Overall_Accuracy"
        ]

        logger.info(
            "\n"
            +
            report[
                display_columns
            ].to_string(
                index=False
            )
        )

        overall_accuracy = (
            report[
                "Overall_Accuracy"
            ].mean()
        )

        logger.info("-" * 60)

        logger.info(
            f"Overall Accuracy: "
            f"{overall_accuracy:.2f}%"
        )

        logger.info(
            "Day-end report completed."
        )

        logger.info("=" * 60)

        return True

    except Exception as e:

        logger.exception(
            f"Day-end report failed: {e}"
        )

        return False


# ==========================================
# ENTRY POINT
# ==========================================

if __name__ == "__main__":

    success = main()

    if success:

        logger.info(
            "Program completed successfully."
        )

    else:

        logger.error(
            "Program completed with errors."
        )
