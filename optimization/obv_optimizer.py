
import pandas as pd
import numpy as np
import itertools
import os

# Configuration
INITIAL_CASH = 1_000_000
TRADE_SIZE = 21
DATA_PATH = "dataset/nifty_data_clean.csv"
RESULTS_PATH = "optimization/optimization_results_obv.csv"
os.makedirs("results", exist_ok=True)

# Load and prepare data
df = pd.read_csv(DATA_PATH, parse_dates=["Date"])
df.set_index("Date", inplace=True)

# Optimization ranges
ma_windows = range(5, 31, 5)  # OBV MA from 5 to 30

# Run optimization
results = []

for ma_window in ma_windows:
    data = df.copy()

    # Calculate OBV
    obv = [0]
    for i in range(1, len(data)):
        if data["Close"].iloc[i] > data["Close"].iloc[i - 1]:
            obv.append(obv[-1] + data["Volume"].iloc[i])
        elif data["Close"].iloc[i] < data["Close"].iloc[i - 1]:
            obv.append(obv[-1] - data["Volume"].iloc[i])
        else:
            obv.append(obv[-1])
    data["OBV"] = obv
    data["OBV_MA"] = data["OBV"].rolling(window=ma_window).mean()

    # Strategy
    cash = INITIAL_CASH
    position = 0
    portfolio_values = []

    for i in range(1, len(data)):
        price = data["Close"].iloc[i]
        if np.isnan(data["OBV_MA"].iloc[i]):
            portfolio_values.append(cash + position * price)
            continue

        # Buy
        if data["OBV"].iloc[i - 1] < data["OBV_MA"].iloc[i - 1] and data["OBV"].iloc[i] > data["OBV_MA"].iloc[i]:
            cost = TRADE_SIZE * price
            if cash >= cost:
                cash -= cost
                position += TRADE_SIZE

        # Sell
        elif data["OBV"].iloc[i - 1] > data["OBV_MA"].iloc[i - 1] and data["OBV"].iloc[i] < data["OBV_MA"].iloc[i]:
            proceeds = TRADE_SIZE * price
            cash += proceeds
            position -= TRADE_SIZE

        portfolio_values.append(cash + position * price)

    # Calculate final metrics
    end_value = portfolio_values[-1]
    n_years = (data.index[-1] - data.index[0]).days / 365.25
    cagr = ((end_value / INITIAL_CASH) ** (1 / n_years)) - 1

    results.append({
        "OBV_MA_WINDOW": ma_window,
        "FINAL_VALUE": round(end_value, 2),
        "CAGR": round(cagr * 100, 2)
    })

# Save results
pd.DataFrame(results).to_csv(RESULTS_PATH, index=False)
print(f"Optimization complete. Results saved to {RESULTS_PATH}")
