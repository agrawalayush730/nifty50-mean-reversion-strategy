import pandas as pd

# Load dataset with indicators
df = pd.read_csv("dataset/nifty_data_with_indicators.csv")
df['Date'] = pd.to_datetime(df['Date'])
df.set_index('Date', inplace=True)

# Strategy settings
initial_capital = 1000000
capital = initial_capital
position_size = 10
in_position = False
buy_price = 0
quantity_held = 0
total_brokerage = 0
trades = []

# Brokerage function
def calculate_brokerage(value):
    return max(20, 0.001 * value)

# Strategy logic
for i in range(1, len(df)):
    row = df.iloc[i]
    price = row['Close']
    date = row.name

    # BUY when price < Lower Band
    if not in_position and price < row['Lower_Band']:
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

    # SELL when price > Upper Band
    elif in_position and price > row['Upper_Band']:
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

# Final net worth
realized_pnl = capital - initial_capital
final_holdings_value = quantity_held * df.iloc[-1]['Close'] if in_position else 0
net_worth = capital + final_holdings_value

# Print trades
for t in trades:
    print(t)

# Summary
print("\n--- Bollinger Band Strategy Summary ---")
print(f"Starting Capital: ₹{initial_capital}")
print(f"Ending Capital: ₹{round(capital, 2)}")
print(f"Final Holdings Value: ₹{round(final_holdings_value, 2)}")
print(f"Total Net Worth: ₹{round(net_worth, 2)}")
print(f"Total Realized PnL: ₹{round(realized_pnl, 2)}")
print(f"Total Brokerage Paid: ₹{round(total_brokerage, 2)}")
