import backtrader as bt
import pandas as pd
import itertools
import os

class MACrossoverOpt(bt.Strategy):
    params = (
        ('fast_ma', 10),
        ('slow_ma', 50),
        ('position_size', 35),
    )

    def __init__(self):
        self.fast = bt.indicators.SimpleMovingAverage(self.data.close, period=self.p.fast_ma)
        self.slow = bt.indicators.SimpleMovingAverage(self.data.close, period=self.p.slow_ma)
        self.crossover = bt.indicators.CrossOver(self.fast, self.slow)
        self.order = None
        self.entry_price = None

    def next(self):
        if self.order:
            return

        if not self.position:
            if self.crossover > 0:
                self.order = self.buy(size=self.p.position_size)
                self.entry_price = self.data.close[0]
        else:
            if self.crossover < 0:
                self.order = self.sell(size=self.p.position_size)

def run_optimization():
    results = []
    fast_range = range(5, 21, 5)       # fast_ma = 5, 10, 15, 20
    slow_range = range(30, 101, 10)    # slow_ma = 30, 40, ..., 100

    for fast, slow in itertools.product(fast_range, slow_range):
        if fast >= slow:
            continue  # skip invalid combinations

        cerebro = bt.Cerebro()
        cerebro.addstrategy(MACrossoverOpt, fast_ma=fast, slow_ma=slow)

        df = pd.read_csv('dataset/nifty_data_with_indicators.csv', parse_dates=['Date'])
        df.set_index('Date', inplace=True)
        data = bt.feeds.PandasData(dataname=df)

        cerebro.adddata(data)
        cerebro.broker.setcash(1000000)
        cerebro.broker.setcommission(commission=0.001)

        start_value = cerebro.broker.getvalue()
        cerebro.run()
        end_value = cerebro.broker.getvalue()

        pnl = end_value - start_value
        cagr = (end_value / start_value) ** (1 / (len(df)/252)) - 1  # Approximate trading years

        results.append({
            'fast_ma': fast,
            'slow_ma': slow,
            'Net PnL': round(pnl, 2),
            'Final Value': round(end_value, 2),
            'CAGR': f"{cagr * 100:.2f}%"
        })

    results_df = pd.DataFrame(results)
    os.makedirs("optimization", exist_ok=True)
    results_df.to_csv("optimization/optimization_results_ma.csv", index=False)
    print("Optimization completed. Results saved to optimization_results_ma.csv")

if __name__ == '__main__':
    run_optimization()
