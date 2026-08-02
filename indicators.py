"""
indicators.py
Technical Indicator Calculations
"""

import pandas as pd

from ta.trend import (
    SMAIndicator,
    EMAIndicator,
    MACD,
    ADXIndicator,
)

from ta.momentum import RSIIndicator

from ta.volatility import (
    BollingerBands,
    AverageTrueRange,
)

from ta.volume import OnBalanceVolumeIndicator


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add all technical indicators.
    """

    df = df.copy()

    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    volume = df["Volume"]

    # -----------------------------
    # Moving Averages
    # -----------------------------
    df["SMA20"] = SMAIndicator(close, 20).sma_indicator()
    df["SMA50"] = SMAIndicator(close, 50).sma_indicator()

    df["EMA20"] = EMAIndicator(close, 20).ema_indicator()
    df["EMA50"] = EMAIndicator(close, 50).ema_indicator()

    # -----------------------------
    # RSI
    # -----------------------------
    df["RSI"] = RSIIndicator(close, 14).rsi()

    # -----------------------------
    # MACD
    # -----------------------------
    macd = MACD(close)

    df["MACD"] = macd.macd()
    df["MACD_SIGNAL"] = macd.macd_signal()
    df["MACD_HIST"] = macd.macd_diff()

    # -----------------------------
    # ADX
    # -----------------------------
    df["ADX"] = ADXIndicator(
        high,
        low,
        close,
        14
    ).adx()

    # -----------------------------
    # ATR
    # -----------------------------
    df["ATR"] = AverageTrueRange(
        high,
        low,
        close,
        14
    ).average_true_range()

    # -----------------------------
    # Bollinger Bands
    # -----------------------------
    bb = BollingerBands(close, 20)

    df["BB_UPPER"] = bb.bollinger_hband()
    df["BB_MIDDLE"] = bb.bollinger_mavg()
    df["BB_LOWER"] = bb.bollinger_lband()
    df["BB_WIDTH"] = bb.bollinger_wband()

    # -----------------------------
    # OBV
    # -----------------------------
    df["OBV"] = OnBalanceVolumeIndicator(
        close,
        volume
    ).on_balance_volume()

    # -----------------------------
    # Returns
    # -----------------------------
    df["DAILY_RETURN"] = close.pct_change()

    df["RETURN_5"] = close.pct_change(5)

    df["RETURN_10"] = close.pct_change(10)

    # -----------------------------
    # Volatility
    # -----------------------------
    df["VOLATILITY"] = (
        close
        .rolling(10)
        .std()
    )

    return df
