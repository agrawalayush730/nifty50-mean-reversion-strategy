import pandas as pd

# Path to your manually cleaned dataset
DATA_PATH = "C:/Projects/nifty50_mean_reversion_backtest/dataset/nifty_data_clean.csv"

def load_and_prepare_data():
    # Load the dataset directly
    df = pd.read_csv(DATA_PATH)
    df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']  # Ensure proper headers

    # Convert 'Date' to datetime and set as index
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)

    # Ensure price columns are numeric
    price_cols = ['Open', 'High', 'Low', 'Close']
    df[price_cols] = df[price_cols].apply(pd.to_numeric, errors='coerce')

    # Drop missing or invalid rows
    df.dropna(inplace=True)

    return df

def add_indicators(df):
    # Calculate 20-day and 90-day Simple Moving Averages
    df['SMA_Fast'] = df['Close'].rolling(window=20).mean()
    df['SMA_Slow'] = df['Close'].rolling(window=90).mean()

    # Calculate Bollinger Bands using 20-day SMA and std dev
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['STD_20'] = df['Close'].rolling(window=20).std()
    df['Upper_Band'] = df['SMA_20'] + 2 * df['STD_20']
    df['Lower_Band'] = df['SMA_20'] - 2 * df['STD_20']

    # Drop rows where any rolling calculation resulted in NaN
    df.dropna(inplace=True)

    return df

def main():
    df = load_and_prepare_data()
    df = add_indicators(df)

    # Display first 30 rows with indicators
    print(df[['Close', 'SMA_Fast', 'SMA_Slow', 'Upper_Band', 'Lower_Band']].head(30))
    df.to_csv("C:/Projects/nifty50_mean_reversion_backtest/dataset/nifty_data_with_indicators.csv")


if __name__ == "__main__":
    main()
