import pandas as pd

# === CONFIGURABLE PARAMETERS ===
initial_capital = 1000000      # Starting capital
position_size = 35              # Units per trade
max_holding_days = 20            # Max number of days to hold
profit_target_pct = 0.03        # 2% profit target (0.02 = 2%)

# === Load Dataset ===
df = pd.read_csv("dataset/nifty_data_with_indicators.csv")
df['Date'] = pd.to_datetime(df['Date'])
df.set_index('Date', inplace=True)



# === Initialize Strategy State ===
capital = initial_capital
in_position = False
buy_price = 0
buy_date = None
quantity_held = 0
total_brokerage = 0
trades = []

def calculate_brokerage(value):
    return 0.001 * value 

# === Run Strategy ===
for i in range(1, len(df)):
    row = df.iloc[i]
    date = row.name
    price = row['Close']

    # --- BUY CONDITION ---
    if not in_position and price < row['Lower_Band']:
        cost = price * position_size
        brokerage = calculate_brokerage(cost)

        if capital >= (cost + brokerage):
            capital -= (cost + brokerage)
            buy_price = price
            buy_date = date
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

    # --- SELL CONDITION ---
    elif in_position:
        holding_days = (date - buy_date).days
        gain_pct = (price - buy_price) / buy_price

        if (
            price > row['SMA_20'] or
            gain_pct >= profit_target_pct or
            holding_days >= max_holding_days
        ):
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

# === Final Net Worth ===
realized_pnl = capital - initial_capital
final_holdings_value = quantity_held * df.iloc[-1]['Close'] if in_position else 0
net_worth = capital + final_holdings_value

# === Print Trades ===
for trade in trades:
    print(trade)

# === Summary ===
print("\n--- Bollinger Band v2 Strategy Summary ---")
print(f"Starting Capital: ₹{initial_capital}")
print(f"Ending Capital: ₹{round(capital, 2)}")
print(f"Final Holdings Value: ₹{round(final_holdings_value, 2)}")
print(f"Total Net Worth: ₹{round(net_worth, 2)}")
print(f"Total Realized PnL: ₹{round(realized_pnl, 2)}")
print(f"Total Brokerage Paid: ₹{round(total_brokerage, 2)}")
