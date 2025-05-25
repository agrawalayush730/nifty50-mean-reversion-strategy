import backtrader as bt
import pandas as pd
import itertools
import os

class BollingerBandOpt(bt.Strategy):
    params = (
        ('sma_period', 20),
        ('devfactor', 2.0),
        ('profit_target', 0.03),
        ('max_hold_days', 10),
        ('position_size', 35),
    )

    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.p.sma_period)
        self.boll = bt.indicators.BollingerBands(self.data.close, period=self.p.sma_period, devfactor=self.p.devfactor)
        self.order = None
        self.entry_price = None
        self.entry_bar = None

    def next(self):
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

            if (
                self.data.close[0] > self.sma[0] or
                gain_pct >= self.p.profit_target or
                holding_days >= self.p.max_hold_days
            ):
                self.order = self.sell(size=self.p.position_size)

def run_bb_optimization():
    results = []
    sma_periods = [15, 20, 25]
    devfactors = [1.5, 2.0, 2.5]
    profit_targets = [0.02, 0.03, 0.04]
    hold_days = [10, 15, 20]

    for sma, dev, pt, hold in itertools.product(sma_periods, devfactors, profit_targets, hold_days):
        cerebro = bt.Cerebro()
        cerebro.addstrategy(
            BollingerBandOpt,
            sma_period=sma,
            devfactor=dev,
            profit_target=pt,
            max_hold_days=hold
        )

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
        days_held = (df.index[-1] - df.index[0]).days
        years = days_held / 365.25
        cagr = (end_value / start_value) ** (1 / years) - 1

        results.append({
            'sma_period': sma,
            'devfactor': dev,
            'profit_target': pt,
            'max_hold_days': hold,
            'Net PnL': round(pnl, 2),
            'Final Value': round(end_value, 2),
            'CAGR': f"{cagr * 100:.2f}%"
        })

    results_df = pd.DataFrame(results)
    os.makedirs("optimization", exist_ok=True)
    results_df.to_csv("optimization/optimization_results_bb.csv", index=False)
    print("BB Optimization completed. Results saved to optimization_results_bb.csv")

if __name__ == '__main__':
    run_bb_optimization()
