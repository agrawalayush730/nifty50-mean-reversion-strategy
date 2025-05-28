
import pandas as pd
import numpy as np
import itertools
import os

# === Config ===
INITIAL_CASH = 1_000_000
TRADE_SIZE = 21
DATA_PATH = "dataset/nifty_data_clean.csv"
RESULTS_PATH = "optimization/optimization_results_rsi.csv"
os.makedirs("results", exist_ok=True)

# === Load and prepare data ===
df = pd.read_csv(DATA_PATH, parse_dates=["Date"])
df.set_index("Date", inplace=True)

# === Optimization ranges ===
rsi_periods = range(7, 22, 2)           # 7 to 21
buy_thresholds = range(20, 41, 5)       # 20 to 40
sell_thresholds = range(60, 81, 5)      # 60 to 80

# === Run Optimization ===
results = []

for period, buy_thres, sell_thres in itertools.product(rsi_periods, buy_thresholds, sell_thresholds):
    data = df.copy()

    # Calculate RSI using Wilder's method
    delta = data["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/period, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period).mean()
    rs = avg_gain / avg_loss
    data["RSI"] = 100 - (100 / (1 + rs))

    cash = INITIAL_CASH
    position = 0
    in_position = False
    portfolio_values = []

    for date, row in data.iterrows():
        price = row["Close"]
        rsi = row["RSI"]
        if np.isnan(rsi):
            portfolio_values.append(cash + position * price)
            continue

        if not in_position and rsi <= buy_thres:
            cost = TRADE_SIZE * price
            if cash >= cost:
                cash -= cost
                position += TRADE_SIZE
                in_position = True

        elif in_position and rsi >= sell_thres:
            proceeds = TRADE_SIZE * price
            cash += proceeds
            position -= TRADE_SIZE
            in_position = False

        portfolio_values.append(cash + position * price)

    # Final stats
    start_value = INITIAL_CASH
    end_value = portfolio_values[-1]
    start_date = data.index[0]
    end_date = data.index[-1]
    n_years = (end_date - start_date).days / 365.25
    cagr = ((end_value / start_value) ** (1 / n_years)) - 1

    results.append({
        "RSI_PERIOD": period,
        "BUY_THRESHOLD": buy_thres,
        "SELL_THRESHOLD": sell_thres,
        "FINAL_VALUE": round(end_value, 2),
        "CAGR": round(cagr * 100, 2)
    })

# Save to CSV
results_df = pd.DataFrame(results)
results_df.to_csv(RESULTS_PATH, index=False)
print(f"Optimization complete. Results saved to {RESULTS_PATH}")
