```python
"""
prediction_history.py

Save daily stock predictions to history.

The file stores:
    Prediction_Date
    Stock
    Open
    High
    Low
    Close

This history is later used by day_end_report.py
to compare predicted prices with actual prices.
"""

import os
import logging
import pandas as pd

from config import REPORT_DIR


logger = logging.getLogger(__name__)


# ======================================================
# HISTORY FILE
# ======================================================

HISTORY_FILE = os.path.join(
    REPORT_DIR,
    "prediction_history.csv"
)


# ======================================================
# SAVE DAILY PREDICTIONS
# ======================================================

def save_prediction_history(
    predictions,
    prediction_date
):
    """
    Save predictions for one trading day.

    Parameters
    ----------
    predictions : list
        List of prediction dictionaries.

    prediction_date : str
        Date for which prediction was generated.
        Format: YYYY-MM-DD
    """

    if not predictions:

        logger.warning(
            "No predictions available to save."
        )

        return False


    try:

        # ------------------------------------------
        # Create reports directory
        # ------------------------------------------

        os.makedirs(
            REPORT_DIR,
            exist_ok=True
        )


        # ------------------------------------------
        # Convert predictions to DataFrame
        # ------------------------------------------

        df = pd.DataFrame(predictions)


        # ------------------------------------------
        # Add prediction date
        # ------------------------------------------

        df.insert(
            0,
            "Prediction_Date",
            prediction_date
        )


        # ------------------------------------------
        # Required columns
        # ------------------------------------------

        required_columns = [
            "Prediction_Date",
            "Stock",
            "Open",
            "High",
            "Low",
            "Close",
        ]


        missing = [
            col
            for col in required_columns
            if col not in df.columns
        ]


        if missing:

            logger.error(
                f"Missing prediction columns: {missing}"
            )

            return False


        df = df[
            required_columns
        ]


        # ------------------------------------------
        # Remove duplicate stock predictions
        # ------------------------------------------

        df = df.drop_duplicates(
            subset=[
                "Prediction_Date",
                "Stock"
            ],
            keep="last"
        )


        # ------------------------------------------
        # Append to existing history
        # ------------------------------------------

        if os.path.exists(HISTORY_FILE):

            try:

                old = pd.read_csv(
                    HISTORY_FILE
                )

                df = pd.concat(
                    [
                        old,
                        df
                    ],
                    ignore_index=True
                )

            except Exception as e:

                logger.warning(
                    f"Could not read existing history: {e}"
                )


        # ------------------------------------------
        # Remove duplicate entries
        # ------------------------------------------

        df = df.drop_duplicates(
            subset=[
                "Prediction_Date",
                "Stock"
            ],
            keep="last"
        )


        # ------------------------------------------
        # Sort history
        # ------------------------------------------

        df = df.sort_values(
            by=[
                "Prediction_Date",
                "Stock"
            ]
        )


        # ------------------------------------------
        # Save CSV
        # ------------------------------------------

        df.to_csv(
            HISTORY_FILE,
            index=False
        )


        logger.info(
            f"Prediction history updated: {HISTORY_FILE}"
        )

        return True


    except Exception as e:

        logger.exception(
            f"Failed to save prediction history: {e}"
        )

        return False
```
