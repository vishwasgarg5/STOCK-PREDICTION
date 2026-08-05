"""
config.py
Central configuration for AI NSE Stock Prediction System
"""

import os

# ==========================================
# PATHS
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CACHE_DIR = os.path.join(BASE_DIR, "cache")
MODEL_DIR = os.path.join(BASE_DIR, "models")

CANDIDATE_MODEL_DIR = os.path.join(
    BASE_DIR,
    "models_candidate"
)

REPORT_DIR = os.path.join(BASE_DIR, "reports")

MODEL_HISTORY_FILE = os.path.join(
    REPORT_DIR,
    "model_history.csv"
)

os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

# ==========================================
# STOCK UNIVERSE
# ==========================================

# Nifty 500 Constituents
NSE_LIST = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"

# ==========================================
# DATA
# ==========================================

PERIOD = "1y"

MIN_HISTORY = 200

MAX_WORKERS = 16

CACHE_EXPIRE_HOURS = 24

# ==========================================
# SCREENER
# ==========================================

TOP_STOCKS = 5

# ==========================================
# MACHINE LEARNING
# ==========================================

RANDOM_STATE = 42

TEST_SIZE = 0.20

N_ESTIMATORS = 300

MAX_DEPTH = 6

LEARNING_RATE = 0.05

SUBSAMPLE = 0.80

COLSAMPLE_BYTREE = 0.80

# ==========================================
# TELEGRAM
# ==========================================

BOT_TOKEN = os.getenv("BOT_TOKEN")

CHAT_ID = os.getenv("CHAT_ID")

# ==========================================
# LOGGING
# ==========================================

LOG_LEVEL = "INFO"
