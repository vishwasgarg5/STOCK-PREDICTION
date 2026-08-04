from accuracy_tracker import (
    get_actual_price,
    evaluate_prediction
)

predicted = {
    "Open": 554.90,
    "High": 573.28,
    "Low": 547.86,
    "Close": 549.86
}

actual = get_actual_price(
    "AIIL",
    "2026-08-04"
)

print(actual)
print(evaluate_prediction(predicted, actual))
