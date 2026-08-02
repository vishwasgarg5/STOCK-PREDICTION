"""
data_loader.py
Download, cache and load NSE stock data
"""

import os
import pickle
import logging
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import yfinance as yf

from config import (
    NSE_LIST,
    PERIOD,
    CACHE_DIR,
    CACHE_EXPIRE_HOURS,
    MAX_WORKERS,
)

logger = logging.getLogger(__name__)


# ==========================================
# NSE SYMBOL LIST
# ==========================================

def get_symbols():
    """
    Download NSE stock symbols
    """

    df = pd.read_csv(NSE_LIST)

    symbols = (
        df["SYMBOL"]
        .dropna()
        .astype(str)
        .str.strip()
        + ".NS"
    )

    return symbols.tolist()


# ==========================================
# CACHE FUNCTIONS
# ==========================================

def cache_path(symbol):
    return os.path.join(CACHE_DIR, f"{symbol}.pkl")


def cache_valid(symbol):

    path = cache_path(symbol)

    if not os.path.exists(path):
        return False

    modified = datetime.fromtimestamp(os.path.getmtime(path))

    age = datetime.now() - modified

    return age < timedelta(hours=CACHE_EXPIRE_HOURS)


def load_cache(symbol):

    path = cache_path(symbol)

    if not os.path.exists(path):
        return None

    with open(path, "rb") as f:
        return pickle.load(f)


def save_cache(symbol, df):

    path = cache_path(symbol)

    with open(path, "wb") as f:
        pickle.dump(df, f)


# ==========================================
# DOWNLOAD ONE STOCK
# ==========================================

def download_stock(symbol, force=False):

    try:

        if not force and cache_valid(symbol):

            df = load_cache(symbol)

            if df is not None:
                return df

        logger.info(f"Downloading {symbol}")

        df = yf.download(
            symbol,
            period=PERIOD,
            progress=False,
            auto_adjust=False,
            threads=False
        )

        if df.empty:
            return None

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df.dropna(inplace=True)

        save_cache(symbol, df)

        return df

    except Exception as e:

        logger.warning(f"{symbol}: {e}")

        return None


# ==========================================
# DOWNLOAD MULTIPLE STOCKS
# ==========================================

def download_multiple(symbols):

    results = {}

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:

        dfs = executor.map(download_stock, symbols)

        for symbol, df in zip(symbols, dfs):

            if df is not None:

                results[symbol] = df

    logger.info(f"Downloaded {len(results)} stocks")

    return results


# ==========================================
# GET ONE STOCK
# ==========================================

def get_stock(symbol):

    return download_stock(symbol)


# ==========================================
# GET MULTIPLE STOCKS
# ==========================================

def get_all_stock_data():

    symbols = get_symbols()

    return download_multiple(symbols)
