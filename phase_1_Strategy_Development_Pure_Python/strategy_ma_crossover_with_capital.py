import pandas as pd

# Load dataset with indicators
df = pd.read_csv("dataset/nifty_data_with_indicators.csv")
df['Date'] = pd.to_datetime(df['Date'])
df.set_index('Date', inplace=True)

# --- Strategy Settings ---
initial_capital = 1000000
capital = initial_capital
position_size = 35  # units per trade
in_position = False
buy_price = 0
quantity_held = 0
trades = []
total_brokerage = 0

# Brokerage function: ₹20 flat or 0.1%, whichever is higher
def calculate_brokerage(value):
    return max(20, 0.001 * value)

# Backtest logic
for i in range(1, len(df)):
    row = df.iloc[i]
    prev = df.iloc[i - 1]
    price = row['Close']
    date = row.name

    # BUY CONDITION
    if not in_position and row['SMA_Fast'] > row['SMA_Slow'] and prev['SMA_Fast'] <= prev['SMA_Slow']:
        cost = price * position_size
        brokerage = calculate_brokerage(cost)

        if capital >= (cost + brokerage):
            capital -= (cost + brokerage)
            buy_price = price
            quantity_held = position_size
            in_position = True
            total_brokerage += brokerage

            trades.append({
                'Date': date,
                'Action': 'BUY',
                'Price': price,
                'Qty': position_size,
                'Brokerage': brokerage,
                'Capital_After': capital
            })

    # SELL CONDITION
    elif in_position and row['SMA_Fast'] < row['SMA_Slow'] and prev['SMA_Fast'] >= prev['SMA_Slow']:
        sell_value = price * quantity_held
        brokerage = calculate_brokerage(sell_value)
        pnl = (price - buy_price) * quantity_held - brokerage
        capital += (sell_value - brokerage)
        in_position = False
        quantity_held = 0
        total_brokerage += brokerage

        trades.append({
            'Date': date,
            'Action': 'SELL',
            'Price': price,
            'Qty': position_size,
            'Brokerage': brokerage,
            'PnL': pnl,
            'Capital_After': capital
        })

# --- Results Summary ---
realized_pnl = capital - initial_capital
final_holdings_value = quantity_held * df.iloc[-1]['Close'] if in_position else 0
net_worth = capital + final_holdings_value

# Print trades
for t in trades:
    print(t)

# Summary
print("\n--- Strategy Summary ---")
print(f"Starting Capital: ₹{initial_capital}")
print(f"Ending Capital: ₹{round(capital, 2)}")
print(f"Final Holdings Value: ₹{round(final_holdings_value, 2)}")
print(f"Total Net Worth: ₹{round(net_worth, 2)}")
print(f"Total Realized PnL: ₹{round(realized_pnl, 2)}")
print(f"Total Brokerage Paid: ₹{round(total_brokerage, 2)}")
