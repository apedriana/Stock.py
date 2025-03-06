import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator, EMAIndicator

def get_stock_data(ticker, start_date, end_date):
    """Fetch stock data for a specific date range from Yahoo Finance."""
    try:
        df = yf.download(ticker, start=start_date, end=end_date, auto_adjust=False)
        # If the columns are a MultiIndex, flatten them:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        # Keep only the desired columns:
        df = df[['Open', 'High', 'Low', 'Close', 'Adj Close']]
        if df.empty:
            print(f"No data found for {ticker} in the given date range.")
            return None
        return df
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None

def add_indicators(df, short_window=14, long_window=50, rsi_window=14):
    """Add RSI, SMA, and EMA indicators to the DataFrame."""
    # Ensure we're using a 1D Series for the Close prices:
    close_series = df["Close"]
    df["SMA"] = SMAIndicator(close_series, window=long_window).sma_indicator()
    df["EMA"] = EMAIndicator(close_series, window=short_window).ema_indicator()
    df["RSI"] = RSIIndicator(close_series, window=rsi_window).rsi()
    return df

def analyze_stock(ticker, start_date, end_date, balance=10000, risk_per_trade=0.01):
    print(f"\n🔍 Analyzing {ticker} from {start_date} to {end_date}...\n")
    
    # Download stock data
    df = get_stock_data(ticker, start_date, end_date)
    if df is None:
        print(f"Could not retrieve stock data for {ticker}. Exiting.")
        return
    
    # Add technical indicators
    df = add_indicators(df)
    
    # Get the most recent data row
    latest_data = df.iloc[-1]
    
    # Force conversion to float to ensure we get scalar values
    try:
        latest_close_price = float(latest_data['Close'])
        latest_rsi = float(latest_data['RSI'])
        latest_sma = float(latest_data['SMA'])
        latest_ema = float(latest_data['EMA'])
    except Exception as e:
        print("Error converting values to float:", e)
        return
    
    # Risk management: calculate position size (using a 5% stop loss assumption)
    stop_loss = 0.05
    position_size = (balance * risk_per_trade) / (stop_loss * latest_close_price)
    
    # Output results with improved formatting
    print("📊 Latest Data for {}:".format(ticker))
    print(f"  - Latest Close Price: ${latest_close_price:.2f}")
    print(f"  - RSI: {latest_rsi:.2f}")
    print(f"  - SMA: ${latest_sma:.2f}")
    print(f"  - EMA: ${latest_ema:.2f}")
    
    print("\n💼 Risk Management:")
    print(f"  - Recommended Position Size: {position_size:.2f} shares based on risk management.")
    
    print("\n⚖️ Signal Analysis:")
    if latest_rsi > 70:
        print("  - 📈 Strong overbought signal (consider selling).")
    elif latest_rsi < 30:
        print("  - 📉 Strong oversold signal (consider buying).")
    else:
        print("  - ⚖️ No strong signal detected.")
    
    print("\n📅 Data range:", start_date, "to", end_date)
    print("📈 Happy Trading!\n")
    
    # Plot data
    plt.figure(figsize=(10, 5))
    plt.plot(df["Close"], label="Close Price", color="blue")
    plt.plot(df["SMA"], label="50-day SMA", color="red", linestyle="dashed")
    plt.plot(df["EMA"], label="14-day EMA", color="green", linestyle="dotted")
    plt.legend()
    plt.title(f"{ticker} Stock Price with Indicators")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.show()

# Example usage:
ticker = input("Enter stock ticker: ").upper()
start_date = input("Enter start date (YYYY-MM-DD): ")
end_date = input("Enter end date (YYYY-MM-DD): ")
analyze_stock(ticker, start_date, end_date)

