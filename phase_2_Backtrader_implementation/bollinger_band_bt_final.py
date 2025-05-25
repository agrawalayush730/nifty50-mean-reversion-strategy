import backtrader as bt
import pandas as pd
import matplotlib.pyplot as plt

class BollingerBandStrategy(bt.Strategy):
    params = (
        ('sma_period', 20),
        ('devfactor', 2.0),              # Wider bands for more trades
        ('profit_target', 0.03),         # 3% profit target
        ('max_hold_days', 15),           # Max holding period
        ('position_size', 40),           # Units per trade
    )

    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.p.sma_period)
        self.boll = bt.indicators.BollingerBands(
            self.data.close, period=self.p.sma_period, devfactor=self.p.devfactor)
        self.order = None
        self.entry_price = None
        self.entry_bar = None
        self.trades = []
        self.equity_curve = []

    def notify_order(self, order):
        if order.status == order.Completed:
            action = 'BUY' if order.isbuy() else 'SELL'
            self.trades.append({
                'Date': self.data.datetime.date(0),
                'Action': action,
                'Price': order.executed.price,
                'Commission': order.executed.comm,
                'Portfolio Value': self.broker.getvalue()
            })
        self.order = None

    def next(self):
        self.equity_curve.append({
            'Date': self.data.datetime.date(0),
            'Portfolio Value': self.broker.getvalue()
        })

        if self.order:
            return

        if not self.position:
            if self.data.close[0] < self.boll.lines.bot[0]:
                self.order = self.buy(size=self.p.position_size)
                self.entry_price = self.data.close[0]
                self.entry_bar = len(self)
        else:
            holding_days = len(self) - self.entry_bar
            gain_pct = (self.data.close[0] - self.entry_price) / self.entry_price

            if (self.data.close[0] > self.sma[0] or
                gain_pct >= self.p.profit_target or
                holding_days >= self.p.max_hold_days):
                self.order = self.sell(size=self.p.position_size)

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(BollingerBandStrategy)

    # Load CSV
    df = pd.read_csv('dataset/nifty_data_with_indicators.csv', parse_dates=['Date'])
    df.set_index('Date', inplace=True)
    data = bt.feeds.PandasData(dataname=df)

    cerebro.adddata(data)
    cerebro.broker.setcash(1000000)
    cerebro.broker.setcommission(commission=0.001)

    print(f"Starting Portfolio Value: ₹{cerebro.broker.getvalue():,.2f}")
    results = cerebro.run()
    final_value = cerebro.broker.getvalue()
    print(f"Final Portfolio Value: ₹{final_value:,.2f}")

    strategy = results[0]
    trades_df = pd.DataFrame(strategy.trades)
    equity_df = pd.DataFrame(strategy.equity_curve)
    equity_df['Date'] = pd.to_datetime(equity_df['Date'])
    equity_df.set_index('Date', inplace=True)
    equity_df = equity_df[~equity_df.index.duplicated(keep='first')]

    # Plot Equity Curve
    equity_df['Portfolio Value'].plot(figsize=(12, 6), title='Equity Curve - Bollinger Band Strategy')
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value (₹)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("results/bollinger_band_equity_curve.png")
    plt.show()

    # Save Trade Log
    trades_df.to_csv("results/bollinger_band_trades_log.csv", index=False)

    # Performance Metrics
    start_val = equity_df['Portfolio Value'].iloc[0]
    end_val = equity_df['Portfolio Value'].iloc[-1]
    duration_years = (equity_df.index[-1] - equity_df.index[0]).days / 365.25
    cagr = (end_val / start_val) ** (1 / duration_years) - 1
    rolling_max = equity_df['Portfolio Value'].cummax()
    drawdown = equity_df['Portfolio Value'] / rolling_max - 1
    max_drawdown = drawdown.min()

    print("\n--- Strategy Performance Summary ---")
    print(f"Starting Capital      : ₹{start_val:,.2f}")
    print(f"Final Portfolio Value : ₹{end_val:,.2f}")
    print(f"Net Profit/Loss       : ₹{end_val - start_val:,.2f}")
    print(f"CAGR                  : {cagr * 100:.2f}%")
    print(f"Max Drawdown          : {max_drawdown * 100:.2f}%")
    print(f"Total Trades Executed : {len(trades_df)}")
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