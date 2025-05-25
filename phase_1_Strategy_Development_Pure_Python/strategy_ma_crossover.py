import pandas as pd

# Load enhanced dataset with indicators
df = pd.read_csv("C:/Projects/nifty50_mean_reversion_backtest/dataset/nifty_data_with_indicators.csv")

# Ensure 'Date' is datetime and set as index
df['Date'] = pd.to_datetime(df['Date'])
df.set_index('Date', inplace=True)

# Initialize trade tracking variables
in_position = False
buy_price = 0
trades = []

# Loop through the DataFrame
for i in range(1, len(df)):
    row = df.iloc[i]
    prev = df.iloc[i - 1]

    # Buy signal: crossover from below to above
    if not in_position and row['SMA_Fast'] > row['SMA_Slow'] and prev['SMA_Fast'] <= prev['SMA_Slow']:
        in_position = True
        buy_price = row['Close']
        trades.append({
            'Date': row.name,
            'Action': 'BUY',
            'Price': buy_price
        })

    # Sell signal: crossover from above to below
    elif in_position and row['SMA_Fast'] < row['SMA_Slow'] and prev['SMA_Fast'] >= prev['SMA_Slow']:
        in_position = False
        sell_price = row['Close']
        trades.append({
            'Date': row.name,
            'Action': 'SELL',
            'Price': sell_price,
            'PnL': sell_price - buy_price
        })

# Output trades
for trade in trades:
    print(trade)

# Summary
total_buys = sum(1 for t in trades if t['Action'] == 'BUY')
total_sells = sum(1 for t in trades if t['Action'] == 'SELL')
total_pnl = sum(t.get('PnL', 0) for t in trades)

print("\nStrategy Summary")
print(f"Total Buy Signals: {total_buys}")
print(f"Total Sell Signals: {total_sells}")
print(f"Total Net PnL: ₹{round(total_pnl, 2)}")
