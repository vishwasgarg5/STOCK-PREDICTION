"""
screener.py
Fast Technical Stock Screener
"""

import logging
import pandas as pd

from concurrent.futures import ThreadPoolExecutor

from config import (
    TOP_STOCKS,
    MAX_WORKERS,
    MIN_HISTORY,
)

from indicators import add_indicators

logger = logging.getLogger(__name__)


# ==========================================
# SCORE ONE STOCK
# ==========================================

def score_stock(symbol, df):

    try:

        if df is None or len(df) < MIN_HISTORY:
            return None

        df = add_indicators(df)

        latest = df.iloc[-1]

        score = 0

        # RSI
        rsi = latest["RSI"]

        if 45 <= rsi <= 60:
            score += 15
        elif 40 <= rsi <= 65:
            score += 8

        # EMA Trend
        if latest["EMA20"] > latest["EMA50"]:
            score += 15

        # MACD
        if latest["MACD"] > latest["MACD_SIGNAL"]:
            score += 15

        # ADX
        if latest["ADX"] > 25:
            score += 15
        elif latest["ADX"] > 20:
            score += 8

        # ATR %
        atr_percent = (
            latest["ATR"] /
            latest["Close"]
        ) * 100

        if atr_percent > 2:
            score += 15
        elif atr_percent > 1:
            score += 8

        # Volume Spike
        avg_volume = df["Volume"].tail(20).mean()

        spike = latest["Volume"] / avg_volume

        if spike > 1.5:
            score += 15
        elif spike > 1.2:
            score += 8

        # Liquidity
        avg_liquidity = df["Volume"].tail(50).mean()

        if avg_liquidity > 2_000_000:
            score += 10
        elif avg_liquidity > 1_000_000:
            score += 5

        return {

            "Stock": symbol,

            "Score": score,

            "RSI": round(float(rsi), 2),

            "ADX": round(float(latest["ADX"]), 2),

            "ATR": round(float(atr_percent), 2),

            "VolumeSpike": round(float(spike), 2),

            "Close": round(float(latest["Close"]), 2)

        }

    except Exception as e:

        logger.debug(f"{symbol}: {e}")

        return None


# ==========================================
# SCREEN ALL STOCKS
# ==========================================

def screen_stocks(stock_data):

    results = []

    with ThreadPoolExecutor(
        max_workers=MAX_WORKERS
    ) as executor:

        futures = [

            executor.submit(
                score_stock,
                symbol,
                df
            )

            for symbol, df in stock_data.items()

        ]

        for future in futures:

            result = future.result()

            if result:

                results.append(result)

    if len(results) == 0:

        logger.error("No stocks scored")

        return []

    df = pd.DataFrame(results)

    df.sort_values(

        by=[

            "Score",

            "ADX",

            "VolumeSpike",

            "RSI"

        ],

        ascending=False,

        inplace=True

    )

    df.reset_index(

        drop=True,

        inplace=True

    )

    logger.info("\nTop Stocks")

    logger.info(df.head(TOP_STOCKS))

    return df.head(TOP_STOCKS)["Stock"].tolist()
