
import backtrader as bt
import pandas as pd
import matplotlib.pyplot as plt
import os

# ==== Configuration ====
FAST = 16
SLOW = 70
SIGNAL = 6
TRADE_SIZE = 21
MIN_DAYS_BETWEEN_TRADES = 2
INITIAL_CASH = 1_000_000
RESULTS_DIR = "results"

# Ensure results folder exists
os.makedirs(RESULTS_DIR, exist_ok=True)

# ==== Define Strategy ====
class MACDStrategy(bt.Strategy):
    params = dict(
        fast=FAST,
        slow=SLOW,
        signal=SIGNAL,
        trade_size=TRADE_SIZE,
        min_days=MIN_DAYS_BETWEEN_TRADES,
    )

    def __init__(self):
        self.macd = bt.ind.MACD(self.data.close,
                                period_me1=self.p.fast,
                                period_me2=self.p.slow,
                                period_signal=self.p.signal)
        self.last_trade = -self.p.min_days
        self.order = None
        self.trade_log = []

    def log_trade(self, action, price, size):
        self.trade_log.append({
            'date': self.datas[0].datetime.date(0).isoformat(),
            'action': action,
            'price': price,
            'size': size,
            'cash': self.broker.get_cash(),
            'value': self.broker.get_value()
        })

    def next(self):
        if self.order:
            return

        if len(self) - self.last_trade < self.p.min_days:
            return

        if not self.position:
            if self.macd.macd[0] > self.macd.signal[0] and self.macd.macd[-1] < self.macd.signal[-1]:
                self.order = self.buy(size=self.p.trade_size, exectype=bt.Order.Close)
                self.last_trade = len(self)
                self.log_trade("BUY", self.data.close[0], self.p.trade_size)
        else:
            if self.macd.macd[0] < self.macd.signal[0] and self.macd.macd[-1] > self.macd.signal[-1]:
                self.order = self.sell(size=self.p.trade_size, exectype=bt.Order.Close)
                self.last_trade = len(self)
                self.log_trade("SELL", self.data.close[0], self.p.trade_size)

    def notify_order(self, order):
        if order.status in [order.Completed, order.Canceled, order.Rejected]:
            self.order = None

    def stop(self):
        df = pd.DataFrame(self.trade_log)
        df.to_csv(f"{RESULTS_DIR}/macd_trades_log.csv", index=False)
        print(f"Trade log saved to {RESULTS_DIR}/macd_trades_log.csv")

# ==== Load Data ====
data = pd.read_csv("dataset/nifty_data_clean.csv", parse_dates=["Date"])
data.set_index("Date", inplace=True)
datafeed = bt.feeds.PandasData(dataname=data)

# ==== Run Backtest ====
cerebro = bt.Cerebro()
cerebro.broker.setcash(INITIAL_CASH)
cerebro.broker.set_coc(True)  # Cheat-on-close enabled
cerebro.adddata(datafeed)
cerebro.addstrategy(MACDStrategy)
results = cerebro.run()
strat = results[0]

# ==== Recalculate Final Value Optimizer Style ====
price_series = data['Close']
cash = INITIAL_CASH
position = 0
equity_curve = []

for date, price in price_series.items():
    trades_today = [t for t in strat.trade_log if t['date'] == date.date().isoformat()]
    for trade in trades_today:
        if trade['action'] == "BUY":
            cost = trade['price'] * trade['size']
            if cash >= cost:
                cash -= cost
                position += trade['size']
        elif trade['action'] == "SELL":
            proceeds = trade['price'] * trade['size']
            cash += proceeds
            position -= trade['size']
    portfolio_value = cash + position * price
    equity_curve.append((date, portfolio_value))

# ==== Compute CAGR ====
start_value = INITIAL_CASH
end_value = equity_curve[-1][1]
n_years = (equity_curve[-1][0] - equity_curve[0][0]).days / 365.25
cagr = ((end_value / start_value) ** (1 / n_years)) - 1

print(f"Initial Capital      : ₹{INITIAL_CASH:,.2f}")
print(f"Final Portfolio Value: ₹{end_value:,.2f}")
print(f"CAGR                 : {cagr*100:.2f}%")

# ==== Save Equity Curve ====
df_equity = pd.DataFrame(equity_curve, columns=["Date", "PortfolioValue"])
df_equity.set_index("Date", inplace=True)
plt.figure(figsize=(12, 6))
plt.plot(df_equity.index, df_equity["PortfolioValue"], label="MACD Optimized Strategy")
plt.title("Equity Curve - Optimizer Aligned MACD Strategy")
plt.xlabel("Date")
plt.ylabel("Portfolio Value (INR)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig(f"{RESULTS_DIR}/macd_equity_curve.png")
plt.close()
print(f"Equity curve saved to {RESULTS_DIR}/macd_equity_curve.png")
