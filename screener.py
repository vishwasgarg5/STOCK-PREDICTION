"""
screener.py
Technical Screener for Nifty 500
"""

import logging

from indicators import add_indicators
from config import TOP_STOCKS

logger = logging.getLogger(__name__)


# ==========================================
# CALCULATE SCORE
# ==========================================

def calculate_score(df):

    try:

        df = add_indicators(df)

        latest = df.iloc[-1]

        score = 0

        # EMA Trend
        if latest["EMA20"] > latest["EMA50"]:
            score += 20

        # RSI
        if 50 <= latest["RSI"] <= 70:
            score += 15

        # MACD
        if latest["MACD"] > latest["MACD_SIGNAL"]:
            score += 20

        # ADX
        if latest["ADX"] > 25:
            score += 15

        # Positive Return
        if latest["RETURN_5"] > 0:
            score += 10

        # OBV Rising
        if len(df) > 1 and df["OBV"].iloc[-1] > df["OBV"].iloc[-2]:
            score += 10

        # Low Volatility
        if latest["VOLATILITY"] < df["VOLATILITY"].mean():
            score += 10

        return score

    except Exception as e:

        logger.warning(f"Screener error: {e}")

        return 0


# ==========================================
# SCREEN STOCKS
# ==========================================

def screen_stocks(stock_data):

    scores = {}

    for symbol, df in stock_data.items():

        scores[symbol] = calculate_score(df)

    ranked = sorted(
        scores.items(),
        key=lambda x: (-x[1], x[0])
    )

    top = [symbol for symbol, score in ranked[:TOP_STOCKS]]

    logger.info("Top Stocks:")

    for symbol, score in ranked[:TOP_STOCKS]:
        logger.info(f"{symbol} | Score: {score}")

    return top
