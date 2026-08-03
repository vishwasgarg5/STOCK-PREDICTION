"""
indicators.py
Technical Indicator Calculations
"""

import pandas as pd

from ta.trend import (
    EMAIndicator,
    MACD,
    ADXIndicator,
)

from ta.momentum import RSIIndicator

from ta.volatility import (
    AverageTrueRange,
)

from ta.volume import OnBalanceVolumeIndicator


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    volume = df["Volume"]

    # EMA
    df["EMA20"] = EMAIndicator(close, window=20).ema_indicator()
    df["EMA50"] = EMAIndicator(close, window=50).ema_indicator()

    # RSI
    df["RSI"] = RSIIndicator(close, window=14).rsi()

    # MACD
    macd = MACD(close)

    df["MACD"] = macd.macd()
    df["MACD_SIGNAL"] = macd.macd_signal()

    # ADX
    df["ADX"] = ADXIndicator(
        high=high,
        low=low,
        close=close,
        window=14
    ).adx()

    # ATR
    df["ATR"] = AverageTrueRange(
        high=high,
        low=low,
        close=close,
        window=14
    ).average_true_range()

    # OBV
    df["OBV"] = OnBalanceVolumeIndicator(
        close=close,
        volume=volume
    ).on_balance_volume()

    # Returns
    df["RETURN_1"] = close.pct_change(1)
    df["RETURN_5"] = close.pct_change(5)

    # Volatility
    df["VOLATILITY"] = close.rolling(10).std()

    return df
