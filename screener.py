# ==========================================
# SCREEN STOCKS
# ==========================================

def screen_stocks(stock_data):

    scores = {}

    for symbol, df in stock_data.items():

        score = calculate_score(df)

        scores[symbol] = score

    # Sort by:
    # 1. Highest score
    # 2. Symbol name (to break ties consistently)
    ranked = sorted(
        scores.items(),
        key=lambda x: (-x[1], x[0])
    )

    top = [
        symbol
        for symbol, score in ranked[:TOP_STOCKS]
    ]

    logger.info("Top Stocks:")

    for symbol, score in ranked[:TOP_STOCKS]:
        logger.info(f"{symbol} | Score: {score}")

    return top
