"""
config.py
Central configuration for AI NSE Stock Prediction System
"""

import os

# ==========================
# PATHS
# ==========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CACHE_DIR = os.path.join(BASE_DIR, "cache")
MODEL_DIR = os.path.join(BASE_DIR, "models")
REPORT_DIR = os.path.join(BASE_DIR, "reports")

os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

# ==========================
# NSE
# ==========================

NSE_LIST = (
    "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
)

# ==========================
# DATA
# ==========================

# 1 year is enough for prediction
PERIOD = "1y"

# minimum candles required
MIN_HISTORY = 150

# ==========================
# SCREENER
# ==========================

TOP_STOCKS = 5

# parallel download workers
MAX_WORKERS = 12

# ==========================
# CACHE
# ==========================

CACHE_EXPIRE_HOURS = 24

# ==========================
# MACHINE LEARNING
# ==========================

RANDOM_STATE = 42

TEST_SIZE = 0.20

N_ESTIMATORS = 300

MAX_DEPTH = 5

LEARNING_RATE = 0.05

SUBSAMPLE = 0.8

COLSAMPLE_BYTREE = 0.8

# ==========================
# TELEGRAM
# ==========================

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ==========================
# LOGGING
# ==========================

LOG_LEVEL = "INFO"
