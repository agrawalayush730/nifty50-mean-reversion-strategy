
import pandas as pd
import numpy as np

# Configuration
INITIAL_CASH = 1_000_000
TRADE_SIZE = 21

# Load data
df = pd.read_csv("dataset/nifty_data_clean.csv", parse_dates=["Date"])
df.set_index("Date", inplace=True)

# Calculate OBV
df["OBV"] = 0
df["OBV"][1:] = np.where(df["Close"].diff()[1:] > 0, df["Volume"][1:], 
                         np.where(df["Close"].diff()[1:] < 0, -df["Volume"][1:], 0)).cumsum()

# Calculate OBV Moving Average (Signal Line)
df["OBV_MA"] = df["OBV"].rolling(window=20).mean()

# Trading Logic
cash = INITIAL_CASH
position = 0
portfolio_values = []

for i in range(1, len(df)):
    price = df["Close"].iloc[i]
    obv = df["OBV"].iloc[i]
    obv_ma = df["OBV_MA"].iloc[i]

    # Skip if MA not ready
    if np.isnan(obv_ma):
        portfolio_values.append(cash + position * price)
        continue

    # Buy condition: OBV crosses above OBV_MA
    if df["OBV"].iloc[i - 1] < df["OBV_MA"].iloc[i - 1] and obv > obv_ma:
        cost = TRADE_SIZE * price
        if cash >= cost:
            cash -= cost
            position += TRADE_SIZE

    # Sell condition: OBV crosses below OBV_MA
    elif df["OBV"].iloc[i - 1] > df["OBV_MA"].iloc[i - 1] and obv < obv_ma:
        proceeds = TRADE_SIZE * price
        cash += proceeds
        position -= TRADE_SIZE

    portfolio_values.append(cash + position * price)

# Final Stats
start_value = INITIAL_CASH
end_value = portfolio_values[-1]
start_date = df.index[0]
end_date = df.index[-1]
n_years = (end_date - start_date).days / 365.25
cagr = ((end_value / start_value) ** (1 / n_years)) - 1

print(f"Initial Capital      : ₹{INITIAL_CASH:,.2f}")
print(f"Final Portfolio Value: ₹{end_value:,.2f}")
print(f"CAGR                 : {cagr * 100:.2f}%")
