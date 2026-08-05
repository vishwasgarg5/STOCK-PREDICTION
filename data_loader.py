import os
import time
import logging
import pickle

from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import yfinance as yf

from config import (
    NSE_LIST,
    PERIOD,
    CACHE_DIR,
    CACHE_EXPIRE_HOURS,
    MAX_WORKERS,
    MIN_HISTORY,
)


# ==========================================
# YFINANCE CACHE
# ==========================================

YF_CACHE = os.path.join(
    CACHE_DIR,
    "yfinance_cache"
)

os.makedirs(
    YF_CACHE,
    exist_ok=True
)

yf.set_tz_cache_location(
    YF_CACHE
)


logger = logging.getLogger(__name__)


# ==========================================
# LOAD NIFTY 500 LIST
# ==========================================

def get_stock_list():

    df = pd.read_csv(NSE_LIST)

    symbols = (
        df["Symbol"]
        .astype(str)
        .str.strip()
        .add(".NS")
        .tolist()
    )

    logger.info(f"Nifty 500 Stocks : {len(symbols)}")

    return symbols


# ==========================================
# CACHE HELPERS
# ==========================================

def cache_path(symbol):

    return os.path.join(
        CACHE_DIR,
        symbol.replace(".NS", "") + ".pkl"
    )


def load_cache(symbol):

    path = cache_path(symbol)

    if not os.path.exists(path):
        return None

    try:

        age = (
            time.time()
            - os.path.getmtime(path)
        ) / 3600

        if age > CACHE_EXPIRE_HOURS:
            return None

        with open(path, "rb") as f:
            return pickle.load(f)

    except Exception as e:

        logger.warning(
            f"Cache error {symbol}: {e}"
        )

        return None


def save_cache(symbol, df):

    with open(cache_path(symbol), "wb") as f:
        pickle.dump(df, f)


# ==========================================
# DOWNLOAD ONE STOCK
# ==========================================

def download_stock(symbol):

    cached = load_cache(symbol)

    if cached is not None:
        return symbol, cached

    try:

        df = yf.download(
            symbol,
            period=PERIOD,
            auto_adjust=False,
            progress=False,
            threads=False,
        )

        if df.empty:
            return symbol, None

        if len(df) < MIN_HISTORY:
            return symbol, None

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df[
            [
                "Open",
                "High",
                "Low",
                "Close",
                "Volume",
            ]
        ].dropna()

        save_cache(symbol, df)

        return symbol, df

    except Exception as e:

        logger.warning(f"{symbol}: {e}")

        return symbol, None


# ==========================================
# DOWNLOAD ALL STOCKS
# ==========================================

def get_all_stock_data():

    symbols = get_stock_list()

    stock_data = {}

    with ThreadPoolExecutor(
        max_workers=MAX_WORKERS
    ) as executor:

        futures = {
            executor.submit(download_stock, s): s
            for s in symbols
        }

        for future in as_completed(futures):

            symbol, df = future.result()

            if df is not None:
                stock_data[symbol] = df

    logger.info(
        f"Downloaded {len(stock_data)} stocks"
    )

    return stock_data
