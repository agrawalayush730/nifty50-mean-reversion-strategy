import pandas as pd
import matplotlib.pyplot as plt
import os

def load_equity_curve(csv_path):
    df = pd.read_csv(csv_path, parse_dates=['Date'])
    df = df.drop_duplicates(subset='Date')
    df = df.set_index('Date')
    return df['Portfolio Value']

def compute_metrics(df):
    start_val = df.iloc[0]
    end_val = df.iloc[-1]
    pnl = end_val - start_val
    duration_years = (df.index[-1] - df.index[0]).days / 365.25
    cagr = (end_val / start_val) ** (1 / duration_years) - 1
    rolling_max = df.cummax()
    drawdown = df / rolling_max - 1
    max_dd = drawdown.min()
    return round(pnl, 2), round(cagr * 100, 2), round(max_dd * 100, 2)

def load_and_compute(csv_path, label):
    df = pd.read_csv(csv_path)
    equity = df[['Date', 'Portfolio Value']].copy()
    equity['Date'] = pd.to_datetime(equity['Date'])
    equity = equity.drop_duplicates(subset='Date')
    equity = equity.set_index('Date')
    pnl, cagr, max_dd = compute_metrics(equity['Portfolio Value'])

    trades = df[df['Action'] == 'SELL']
    wins, losses = 0, 0
    position_open = False
    entry_price = 0.0

    for _, row in df.iterrows():
        if row['Action'] == 'BUY':
            entry_price = row['Price']
            position_open = True
        elif row['Action'] == 'SELL' and position_open:
            if row['Price'] - entry_price > 0:
                wins += 1
            else:
                losses += 1
            position_open = False

    win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
    return {
        'Label': label,
        'Final Value': round(equity['Portfolio Value'].iloc[-1], 2),
        'Net PnL': pnl,
        'CAGR (%)': cagr,
        'Max Drawdown (%)': max_dd,
        'Trades': len(trades),
        'Win Rate (%)': round(win_rate, 2)
    }, equity

def plot_equity_curves(ma_curve, bb_curve):
    plt.figure(figsize=(12, 6))
    ma_curve.plot(label='MA Crossover')
    bb_curve.plot(label='Bollinger Band')
    plt.title('Equity Curve Comparison')
    plt.xlabel('Date')
    plt.ylabel('Portfolio Value (₹)')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    os.makedirs("results", exist_ok=True)
    plt.savefig("results/strategy_comparison_equity.png")
    plt.show()

def main():
    ma_metrics, ma_equity = load_and_compute('results/ma_crossover_trades_log.csv', 'MA Crossover')
    bb_metrics, bb_equity = load_and_compute('results/bollinger_band_trades_log.csv', 'Bollinger Band')
    plot_equity_curves(ma_equity['Portfolio Value'], bb_equity['Portfolio Value'])

    comparison_df = pd.DataFrame([ma_metrics, bb_metrics])
    print("\n=== Strategy Comparison Summary ===\n")
    print(comparison_df.to_string(index=False))
    comparison_df.to_csv("results/strategy_comparison_summary.csv", index=False)

if __name__ == '__main__':
    main()
