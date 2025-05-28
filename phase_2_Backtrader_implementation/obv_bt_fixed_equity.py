
import backtrader as bt
import pandas as pd
import matplotlib.pyplot as plt
import os

# === Custom OBV Indicator ===
class OBV(bt.Indicator):
    lines = ('obv',)
    plotinfo = dict(subplot=True)

    def __init__(self):
        self.lines.obv = bt.If(self.data.close > self.data.close(-1),
                               self.data.volume,
                               bt.If(self.data.close < self.data.close(-1),
                                     -self.data.volume,
                                     0))
        self.lines.obv = bt.indicators.SumN(self.lines.obv, period=len(self.data))

# === OBV Strategy with Equity Tracking ===
class OBVStrategy(bt.Strategy):
    params = dict(
        ma_window=5,
        trade_size=21
    )

    def __init__(self):
        self.obv = OBV(self.data).obv
        self.obv_ma = bt.indicators.SMA(self.obv, period=self.p.ma_window)
        self.order = None
        self.portfolio_values = []

    def next(self):
        if self.order:
            return

        self.portfolio_values.append(self.broker.getvalue())

        if not self.position:
            if self.obv[-1] < self.obv_ma[-1] and self.obv[0] > self.obv_ma[0]:
                self.order = self.buy(size=self.p.trade_size)
        else:
            if self.obv[-1] > self.obv_ma[-1] and self.obv[0] < self.obv_ma[0]:
                self.order = self.sell(size=self.p.trade_size)

    def notify_order(self, order):
        if order.status in [order.Completed]:
            self.order = None

# Analyzer for trade logs
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

# Backtest Setup
cerebro = bt.Cerebro()
cerebro.broker.setcash(1_000_000)

# Load data
df = pd.read_csv("dataset/nifty_data_clean.csv", parse_dates=["Date"])
df.set_index("Date", inplace=True)
data = bt.feeds.PandasData(dataname=df)

cerebro.adddata(data)
cerebro.addstrategy(OBVStrategy)
cerebro.addanalyzer(TradeLogger, _name='trade_logger')

results = cerebro.run()
strat = results[0]
final_value = cerebro.broker.getvalue()

# Calculate CAGR
start_value = 1_000_000
start_date = df.index[0]
end_date = df.index[-1]
n_years = (end_date - start_date).days / 365.25
cagr = ((final_value / start_value) ** (1 / n_years)) - 1

# Output results
print(f"Initial Capital      : ₹{start_value:,.2f}")
print(f"Final Portfolio Value: ₹{final_value:,.2f}")
print(f"CAGR                 : {cagr * 100:.2f}%")

# Save results
os.makedirs("results", exist_ok=True)
pd.DataFrame(strat.analyzers.trade_logger.get_analysis()).to_csv("results/obv_trades_log.csv", index=False)

# Plot equity curve manually
plt.figure(figsize=(10, 5))
plt.plot(strat.portfolio_values)
plt.title("Equity Curve - OBV Strategy (Manual Tracking)")
plt.xlabel("Time Step")
plt.ylabel("Portfolio Value")
plt.grid(True)
plt.savefig("results/obv_equity_curve.png")
plt.close()
