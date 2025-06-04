import pandas as pd
import numpy as np

# Config
INITIAL_CASH = 1_000_000
TRADE_SIZE = 21
RSI_PERIOD = 14
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70

# Load data
df = pd.read_csv("dataset/nifty_data_clean.csv", parse_dates=["Date"])
df.set_index("Date", inplace=True)

# Calculate RSI using Wilder's smoothing
delta = df["Close"].diff()
gain = delta.clip(lower=0)
loss = -delta.clip(upper=0)
avg_gain = gain.ewm(alpha=1/RSI_PERIOD, min_periods=RSI_PERIOD, adjust=False).mean()
avg_loss = loss.ewm(alpha=1/RSI_PERIOD, min_periods=RSI_PERIOD, adjust=False).mean()
rs = avg_gain / avg_loss
df["RSI"] = 100 - (100 / (1 + rs))

# Strategy logic
cash = INITIAL_CASH
position = 0
portfolio_values = []
in_position = False

for date, row in df.iterrows():
    price = row["Close"]
    rsi = row["RSI"]

    if np.isnan(rsi):
        portfolio_values.append(cash + position * price)
        continue

    # Buy if RSI <= 30 and not in position
    if not in_position and rsi <= RSI_OVERSOLD:
        cost = TRADE_SIZE * price
        if cash >= cost:
            cash -= cost
            position += TRADE_SIZE
            in_position = True

    # Sell if RSI >= 70 and in position
    elif in_position and rsi >= RSI_OVERBOUGHT:
        proceeds = TRADE_SIZE * price
        cash += proceeds
        position -= TRADE_SIZE
        in_position = False

    portfolio_values.append(cash + position * price)

# Calculate final stats 
start_value = INITIAL_CASH
end_value = portfolio_values[-1]
start_date = df.index[0]
end_date = df.index[-1]
n_years = (end_date - start_date).days / 365.25
cagr = ((end_value / start_value) ** (1 / n_years)) - 1 if n_years > 0 else 0

print(f"Initial Capital      : ₹{start_value:,.2f}")
print(f"Final Portfolio Value: ₹{end_value:,.2f}")
print(f"CAGR                 : {cagr * 100:.2f}%")
