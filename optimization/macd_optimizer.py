import pandas as pd
import numpy as np
from itertools import product
from datetime import timedelta
from tqdm import tqdm

# Load dataset
df = pd.read_csv("dataset/nifty_data_clean.csv", parse_dates=["Date"])
df.set_index("Date", inplace=True)

# Define optimization ranges
fast_ema_range = range(8, 19,2)
slow_ema_range = range(20, 81,10)
signal_ema_range = range(6, 16, 2)
min_days_range = range(2, 11,2)
trade_size_range = range(1, 51, 10)

initial_cash = 1_000_000

best_config = {}
best_cagr = -np.inf

results = []

# Optimization loop
search_space = list(product(fast_ema_range, slow_ema_range, signal_ema_range, min_days_range, trade_size_range))
for fast, slow, signal, min_days, trade_size in tqdm(search_space, desc="Optimizing MACD"):

    if slow <= fast:
        continue

    data = df.copy()
    data['EMA_fast'] = data['Close'].ewm(span=fast, adjust=False).mean()
    data['EMA_slow'] = data['Close'].ewm(span=slow, adjust=False).mean()
    data['MACD'] = data['EMA_fast'] - data['EMA_slow']
    data['Signal'] = data['MACD'].ewm(span=signal, adjust=False).mean()

    data['Buy_Signal'] = (data['MACD'] > data['Signal']) & (data['MACD'].shift(1) <= data['Signal'].shift(1))
    data['Sell_Signal'] = (data['MACD'] < data['Signal']) & (data['MACD'].shift(1) >= data['Signal'].shift(1))

    cash = initial_cash
    shares = 0
    last_trade_date = data.index[0] - timedelta(days=min_days)
    portfolio_values = []

    for date, row in data.iterrows():
        price = row['Close']

        if row['Buy_Signal'] and (date - last_trade_date).days >= min_days:
            cost = trade_size * price
            if cash >= cost:
                shares += trade_size
                cash -= cost
                last_trade_date = date

        elif row['Sell_Signal'] and (date - last_trade_date).days >= min_days:
            if shares >= trade_size:
                cash += trade_size * price
                shares -= trade_size
                last_trade_date = date

        portfolio_value = cash + shares * price
        portfolio_values.append(portfolio_value)

    if len(portfolio_values) == 0:
        continue

    final_value = portfolio_values[-1]
    duration_years = (data.index[-1] - data.index[0]).days / 365.25
    cagr = ((final_value / initial_cash) ** (1 / duration_years)) - 1

    results.append({
        'fast_ema': fast,
        'slow_ema': slow,
        'signal_ema': signal,
        'min_days_between_trades': min_days,
        'trade_size': trade_size,
        'final_value': final_value,
        'cagr': cagr
    })

# Save all results to CSV
results_df = pd.DataFrame(results)
results_df.to_csv("optimization/optimization_results_macd.csv", index=False)
print("All optimization results saved to optimization/optimization_results_macd.csv")
