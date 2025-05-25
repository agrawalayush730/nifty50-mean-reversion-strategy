import backtrader as bt
import pandas as pd
import matplotlib.pyplot as plt

class MACrossoverStrategy(bt.Strategy):
    params = (
        ('fast_period', 20),
        ('slow_period', 90),
        ('position_size', 35),
    )

    def __init__(self):
        self.order = None
        self.fast_ma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.p.fast_period)
        self.slow_ma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.p.slow_period)
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)
        self.trades = []

    def notify_order(self, order):
        if order.status in [order.Completed]:
            action = 'BUY' if order.isbuy() else 'SELL'
            self.trades.append({
                'Date': self.data.datetime.date(0),
                'Action': action,
                'Price': order.executed.price,
                'Cost': order.executed.value,
                'Commission': order.executed.comm,
                'Portfolio Value': self.broker.getvalue()
            })
        self.order = None

    def next(self):
        if self.order:
            return
        if not self.position and self.crossover > 0:
            self.order = self.buy(size=self.p.position_size)
        elif self.position and self.crossover < 0:
            self.order = self.sell(size=self.p.position_size)

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(MACrossoverStrategy)

    df = pd.read_csv('dataset/nifty_data_with_indicators.csv', parse_dates=['Date'])
    df.set_index('Date', inplace=True)
    data = bt.feeds.PandasData(dataname=df)

    cerebro.adddata(data)
    cerebro.broker.setcash(1000000)
    cerebro.broker.setcommission(commission=0.001)

    print(f"Starting Capital: ₹{cerebro.broker.getvalue():.2f}")
    results = cerebro.run()
    final_value = cerebro.broker.getvalue()
    print(f"Final Portfolio Value: ₹{final_value:.2f}")

    strategy = results[0]
    trades_df = pd.DataFrame(strategy.trades)
    trades_df.to_csv("results/ma_crossover_trades_log.csv", index=False)

    # Create Equity Curve
    equity_df = trades_df[['Date', 'Portfolio Value']].copy()
    equity_df['Date'] = pd.to_datetime(equity_df['Date'])
    equity_df.set_index('Date', inplace=True)
    equity_df = equity_df[~equity_df.index.duplicated(keep='first')]

    # === Calculate Metrics ===
    if not equity_df.empty:
        start_val = equity_df['Portfolio Value'].iloc[0]
        end_val = equity_df['Portfolio Value'].iloc[-1]
        years = (equity_df.index[-1] - equity_df.index[0]).days / 365.25

        # CAGR
        cagr = (end_val / start_val) ** (1 / years) - 1 if years > 0 else 0

        # Max Drawdown
        rolling_max = equity_df['Portfolio Value'].cummax()
        drawdown = equity_df['Portfolio Value'] / rolling_max - 1
        max_drawdown = drawdown.min()

        # Print Summary
        print("\n--- Strategy Performance Summary ---")
        print(f"Starting Capital      : ₹{start_val:,.2f}")
        print(f"Final Portfolio Value : ₹{end_val:,.2f}")
        print(f"Net Profit/Loss       : ₹{end_val - start_val:,.2f}")
        print(f"CAGR                  : {cagr * 100:.2f}%")
        print(f"Max Drawdown          : {max_drawdown * 100:.2f}%")
        print(f"Total Trades Executed : {len(trades_df)}")

        pnl = end_val - start_val
        print(f"Net PnL: ₹{pnl:.2f}")
        print(f"Total Trades: {len(trades_df)}")
        wins = 0
        losses = 0
        position_open = False
        entry_price = 0.0

        for i, row in trades_df.iterrows():
            if row['Action'] == 'BUY':
                entry_price = row['Price']
                position_open = True
            elif row['Action'] == 'SELL' and position_open:
                exit_price = row['Price']
                pnl = exit_price - entry_price
                if pnl > 0:
                    wins += 1
                else:
                    losses += 1
                position_open = False

        total_closed_trades = wins + losses
        win_rate = (wins / total_closed_trades) * 100 if total_closed_trades > 0 else 0.0

        print(f"Winning Trades         : {wins}")
        print(f"Losing Trades          : {losses}")
        print(f"Win Rate               : {win_rate:.2f}%")
        # Equity curve
        equity_df['Portfolio Value'].plot(figsize=(12, 6), title='Equity Curve - MA Crossover')
        plt.xlabel("Date")
        plt.ylabel("Portfolio Value (₹)")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig("results/ma_crossover_equity_curve.png")
        plt.show()
    else:
        print("No trades were executed. Equity curve and metrics not available.")
