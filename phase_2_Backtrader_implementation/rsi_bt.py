import backtrader as bt
import pandas as pd
import os
import matplotlib.pyplot as plt

# === Strategy ===
class RSIStrategy(bt.Strategy):
    params = dict(
        rsi_period=21,
        buy_threshold=40,
        sell_threshold=80,
        trade_size=21
    )

    def __init__(self):
        self.rsi = bt.ind.RSI(period=self.p.rsi_period)
        self.order = None
        self.equity_curve = []

    def next(self):
        self.equity_curve.append(self.broker.getvalue())
        if self.order:
            return  # waiting for pending order

        if not self.position:
            if self.rsi[0] < self.p.buy_threshold:
                self.order = self.buy(size=self.p.trade_size)
        else:
            if self.rsi[0] > self.p.sell_threshold:
                self.order = self.sell(size=self.p.trade_size)

    def notify_order(self, order):
        if order.status in [order.Completed]:
            self.order = None

# Trade log tracking
class TradeLogger(bt.Analyzer):
    def __init__(self):
        self.trades = []

    def notify_trade(self, trade):
        if trade.isclosed:
            self.trades.append({
                'date': trade.close_datetime().date(),
                'pnl': trade.pnl,
                'price': trade.price,
                'size': trade.size
            })

    def get_analysis(self):
        return self.trades

# === Backtest Setup ===
cerebro = bt.Cerebro()
cerebro.broker.setcash(1_000_000)

# Load data
df = pd.read_csv("dataset/nifty_data_clean.csv", parse_dates=["Date"])
df.set_index("Date", inplace=True)
data = bt.feeds.PandasData(dataname=df)

cerebro.adddata(data)
cerebro.addstrategy(RSIStrategy)
cerebro.addanalyzer(TradeLogger, _name='trade_logger')

# Run
results = cerebro.run()
strat = results[0]
final_value = cerebro.broker.getvalue()

# Calculate CAGR
start_value = 1_000_000
start_date = df.index[0]
end_date = df.index[-1]
n_years = (end_date - start_date).days / 365.25
cagr = ((final_value / start_value) ** (1 / n_years)) - 1

# Print Results
print(f"Initial Capital      : ₹{start_value:,.2f}")
print(f"Final Portfolio Value: ₹{final_value:,.2f}")
print(f"CAGR                 : {cagr * 100:.2f}%")

# Save trade log
os.makedirs("results", exist_ok=True)
pd.DataFrame(strat.analyzers.trade_logger.get_analysis()).to_csv("results/rsi_trades_log.csv", index=False)

# Save equity curve
plt.figure(figsize=(10, 5))
plt.plot(strat.equity_curve)
plt.title("Equity Curve - RSI Strategy")
plt.xlabel("Time Step")
plt.ylabel("Portfolio Value")
plt.grid(True)
plt.savefig("results/rsi_equity_curve.png")
plt.close()
