
# 📈 NIFTY50 Mean Reversion Strategy Backtest

This project implements and compares multiple algorithmic trading strategies on the NIFTY50 index using 10 years of daily data (2015–2024). It includes pure Python logic, full Backtrader integration, parameter optimization, and performance visualization with trade logs and equity curves.

---

## 🚀 Strategies Implemented

### 1. MA Crossover Strategy (Trend Following)
- **Buy Signal:** Fast SMA crosses above Slow SMA
- **Sell Signal:** Fast SMA crosses below Slow SMA
- **Final Tuned Params:** `Fast SMA = 20`, `Slow SMA = 90`, `Position Size = 35`

### 2. Bollinger Band Strategy (Mean Reversion)
- **Buy Signal:** Price drops below Lower Band
- **Sell Signal:** Exit on 3% profit target or after 15 days
- **Final Tuned Params:** `SMA = 20`, `DevFactor = 2.0`, `Profit Target = 3%`, `Hold Days = 15`

### 3. MACD Strategy
- **Buy Signal:** MACD Line crosses above Signal Line (with min days gap)
- **Sell Signal:** MACD Line crosses below Signal Line
- **Optimized Params:** `Fast EMA = 14`, `Slow EMA = 70`, `Signal EMA = 10`, `Min Gap = 4 Days`, `Trade Size = 21`

### 4. RSI Strategy
- **Buy Signal:** RSI goes below 40 and comes back above
- **Sell Signal:** RSI goes above 80 and falls back
- **Optimized Params:** `RSI Period = 21`, `Buy Threshold = 40`, `Sell Threshold = 80`

### 5. OBV Strategy (Volume-Based)
- **Buy Signal:** OBV crosses above its moving average
- **Sell Signal:** OBV crosses below its moving average
- **Optimized Params:** `OBV MA Window = 5`, `Trade Size = 21`

---

## 📊 Final Performance Summary

| Strategy         | Final Value     | Net PnL        | CAGR   | Trades | Win Rate |
|------------------|------------------|----------------|--------|--------|----------|
| MA Crossover     | ₹14,27,797.08    | ₹4,27,797.08   | 4.24%  | 12     | 75.00%   |
| Bollinger Band   | ₹11,96,099.71    | ₹1,96,099.71   | 1.95%  | 47     | 82.98%   |
| MACD             | ₹11,70,453.00    | ₹1,70,453.00   | 1.71%  | ~12    | ~66%     |
| RSI              | ₹13,34,019.72    | ₹3,34,019.72   | 2.93%  | 1      | 100.0%   |
| OBV              | ₹12,23,770.76    | ₹2,23,770.76   | 2.04%  | 5      | 60.0%    |

---

## 🧰 Tech Stack

- **Python 3.10+**
- **Backtrader** – backtesting framework
- **Matplotlib** – visualization
- **Pandas** – data analysis
- **yFinance** – NIFTY50 data acquisition
- **CSV / PNG outputs** – trade logs and equity curves

---

## 📂 Folder Structure

```
NIFTY50_MEAN_REVERSION_BACKTEST/
│
├── dataset/                             # Cleaned NIFTY50 dataset
├── optimization/                        # Parameter tuning files (MACD, RSI, OBV)
├── results/                             # Equity curves, trade logs
├── phase_1_Strategy_Development_Pure_Python/
├── phase_2_Backtrader_implementation/
│   ├── ma_crossover_bt.py
│   ├── bollinger_band_bt_final.py
│   ├── macd_bt.py
│   ├── rsi_bt.py
│   ├── obv_bt_fixed_equity.py
│
├── strategy_comparison.py
├── indicators.py                        # Custom indicators (if any)
├── README.md
```

---

## ▶️ How to Run

1. **Install dependencies**:
```bash
pip install pandas matplotlib backtrader yfinance
```

2. **Load or generate dataset**:
```python
import yfinance as yf
df = yf.download("^NSEI", start="2015-01-01", end="2025-01-01")
df.to_csv("dataset/nifty_data_clean.csv")
```

3. **Run strategies individually**:
```bash
python phase_2_Backtrader_implementation/ma_crossover_bt.py
python phase_2_Backtrader_implementation/bollinger_band_bt_final.py
python phase_2_Backtrader_implementation/macd_bt.py
python phase_2_Backtrader_implementation/rsi_bt.py
python phase_2_Backtrader_implementation/obv_bt_fixed_equity.py
```

4. **Compare strategies (optional)**:
```bash
python strategy_comparison.py
```

---

## 📈 Sample Outputs

- `results/ma_crossover_equity_curve.png`
- `results/bollinger_band_equity_curve.png`
- `results/macd_equity_curve.png`
- `results/rsi_equity_curve.png`
- `results/obv_equity_curve.png`
- `results/<strategy>_trades_log.csv`

---

## 👨‍💻 Author

**Ayush Agrawal**  
Bachelor of Data Science – SP Jain School of Global Management  
[GitHub Profile](https://github.com/agrawalayush730)

---

## 📎 License

Usage is permitted for portfolio review, research, or educational demonstration.
Commercial use, redistribution, or modification without attribution is discouraged.