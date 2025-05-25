
# 📈 NIFTY50 Mean Reversion Strategy Backtest

This project implements and compares two algorithmic trading strategies on the NIFTY50 index using 10 years of daily data (2015–2024). It includes pure Python logic, full Backtrader integration, parameter optimization, and side-by-side performance tracking.

---

## 🚀 Strategies Implemented

### 1. MA Crossover Strategy (Trend Following)
- **Buy Signal:** When Fast SMA crosses above Slow SMA
- **Sell Signal:** When Fast SMA crosses below Slow SMA
- **Final Tuned Params:** `Fast SMA = 20`, `Slow SMA = 90`, `Position Size = 35`

### 2. Bollinger Band Strategy (Mean Reversion)
- **Buy Signal:** Price drops below Lower Band
- **Sell Signal:** Exit if price hits profit target or max holding days reached
- **Final Tuned Params:** `SMA = 20`, `DevFactor = 2.0`, `Profit Target = 3%`, `Hold Days = 15`

---

## 🧰 Tech Stack

- **Python**
- **Backtrader** (Backtesting framework)
- **Matplotlib** (Charts)
- **Pandas** (Data wrangling)
- **yFinance** (Data download)
- **CSV & PNG outputs** for logs and visuals

---

## 📊 Final Performance Summary

| Metric            | MA Crossover     | Bollinger Band    |
|-------------------|------------------|--------------------|
| Final Value       | ₹14,27,797.08    | ₹11,96,099.71      |
| Net PnL           | ₹4,28,242.21     | ₹1,97,003.51       |
| CAGR              | 4.24%            | 1.95%              |
| Max Drawdown      | -5.18%           | -14.45%            |
| Total Trades      | 12               | 47                 |
| Win Rate          | 75.0%            | 82.98%             |

---

## 📂 Folder Structure

```
NIFTY50_MEAN_REVERSION_BACKTEST/
│
├── dataset/                             # Clean and derived datasets
├── optimization/                        # MA/BB parameter tuning
├── phase_1_Strategy_Development_Pure_Python/
├── phase_2_Backtrader_implementation/
├── results/                             # Equity curves, logs, comparison outputs
│
├── indicators.py                        # Custom indicators
├── strategy_comparison.py              # Dashboard to compare MA vs BB
├── README.md
```

---

## ▶️ How to Run

1. **Install dependencies**:
```bash
pip install pandas matplotlib backtrader yfinance
```

2. **Download data** (already included):
```python
import yfinance as yf
df = yf.download("^NSEI", start="2015-01-01", end="2025-01-01")
df.to_csv("dataset/nifty_data_clean.csv")
```

3. **Run Backtests**:
```bash
python phase_2_Backtrader_implementation/ma_crossover_bt.py
python phase_2_Backtrader_implementation/bollinger_band_bt_final.py
```

4. **Compare strategies**:
```bash
python strategy_comparison.py
```

---

## 📈 Output Samples

- `results/ma_crossover_equity_curve.png`
- `results/bollinger_band_equity_curve.png`
- `results/strategy_comparison_equity.png`
- `results/strategy_comparison_summary.csv`

---

## 📌 Author

**Ayush Agrawal**  
Bachelor of Data Science — SP Jain School of Global Management  
[GitHub](https://github.com/agrawalayush730)

---

## 📎 License

This project is released under the MIT License.
Usage is permitted for portfolio review, research, or educational demonstration.
Commercial use, redistribution, or modification without attribution is discouraged.
