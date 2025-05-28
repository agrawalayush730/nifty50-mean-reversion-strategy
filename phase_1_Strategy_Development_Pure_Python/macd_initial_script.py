import pandas as pd
import numpy as np

# Load your NIFTY50 data
df = pd.read_csv("dataset/nifty_data_clean.csv", parse_dates=['Date'])
df.set_index('Date', inplace=True)

# --- MACD Calculations ---
df['EMA_12'] = df['Close'].ewm(span=16, adjust=False).mean()
df['EMA_26'] = df['Close'].ewm(span=70, adjust=False).mean()
df['MACD_Line'] = df['EMA_12'] - df['EMA_26']
df['Signal_Line'] = df['MACD_Line'].ewm(span=6, adjust=False).mean()
df['MACD_Histogram'] = df['MACD_Line'] - df['Signal_Line']

# --- Generate Buy/Sell Signals ---
df['Signal'] = 0
df['Signal'] = np.where(df['MACD_Line'] > df['Signal_Line'], 1, 0)
df['Position'] = df['Signal'].diff()  # 1 = buy, -1 = sell

# --- Simulate Trades ---
initial_cash = 1_000_000
cash = initial_cash
shares = 0
portfolio_values = []

for i in range(1, len(df)):
    price = df['Close'].iloc[i]
    signal = df['Position'].iloc[i]

    # Buy signal
    if signal == 1:
        shares = cash // price
        cash -= shares * price

    # Sell signal
    elif signal == -1 and shares > 0:
        cash += shares * price
        shares = 0

    # Portfolio value at each step
    portfolio_value = cash + shares * price
    portfolio_values.append(portfolio_value)

# --- Final Metrics ---
final_value = portfolio_values[-1]
net_pnl = final_value - initial_cash
start_date = df.index[1]
end_date = df.index[-1]
years = (end_date - start_date).days / 365.25
cagr = ((final_value / initial_cash) ** (1 / years)) - 1

# --- Print Results ---
print(f"Initial Capital      : ₹{initial_cash:,.2f}")
print(f"Final Portfolio Value: ₹{final_value:,.2f}")
print(f"Net Profit/Loss      : ₹{net_pnl:,.2f}")
print(f"CAGR                 : {cagr*100:.2f}%")
