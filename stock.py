import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator, EMAIndicator

def get_stock_data(ticker, start_date, end_date):
    """Fetch stock data for a specific date range from Yahoo Finance."""
    try:
        df = yf.download(ticker, start=start_date, end=end_date, auto_adjust=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df[['Open', 'High', 'Low', 'Close', 'Adj Close']]
        if df.empty:
            print(f"No data found for {ticker} in the given date range.")
            return None
        return df
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None

def add_indicators(df, sma_window, ema_window, rsi_window=14):
    """Add RSI, SMA, and EMA indicators to the DataFrame."""
    close_series = df["Close"]
    df["SMA"] = SMAIndicator(close_series, window=sma_window).sma_indicator()
    df["EMA"] = EMAIndicator(close_series, window=ema_window).ema_indicator()
    df["RSI"] = RSIIndicator(close_series, window=rsi_window).rsi()
    return df

def analyze_stock(ticker, start_date, end_date, portfolio, trading_horizon="short"):
    print(f"\n🔍 Analyzing {ticker} from {start_date} to {end_date}...\n")
    
    # Define SMA and EMA window based on trading horizon
    if trading_horizon == "short":
        sma_window = 14
        ema_window = 14
    elif trading_horizon == "medium":
        sma_window = 50
        ema_window = 50
    elif trading_horizon == "long":
        sma_window = 200
        ema_window = 200
    else:
        print("Invalid trading horizon. Defaulting to short-term.")
        sma_window = 14
        ema_window = 14
    
    # Download stock data
    df = get_stock_data(ticker, start_date, end_date)
    if df is None:
        print(f"Could not retrieve stock data for {ticker}. Exiting.")
        return
    
    # Add technical indicators
    df = add_indicators(df, sma_window, ema_window)
    
    # Get the most recent data row
    latest_data = df.iloc[-1]
    
    # Risk management
    risk_per_trade = 0.01
    stop_loss = 0.05
    position_size = (portfolio * risk_per_trade) / (stop_loss * latest_data['Close'])
    
    # Output results with improved formatting
    print("📊 Latest Data for {}:".format(ticker))
    print(f"  - Latest Close Price: ${latest_data['Close']:.2f}")
    print(f"  - RSI: {latest_data['RSI']:.2f}")
    print(f"  - SMA: ${latest_data['SMA']:.2f}")
    print(f"  - EMA: ${latest_data['EMA']:.2f}")
    print(f"\n💼 Risk Management:")
    print(f"  - Portfolio Value: ${portfolio}")
    print(f"  - 1% Risk per Trade: ${portfolio * risk_per_trade:.2f}")
    print(f"  - Recommended Position Size: {position_size:.2f} shares based on risk management.")
    
    # Signal analysis
    print("\n⚖️ Signal Analysis:")
    if latest_data['RSI'] > 70:
        print("  - 📈 Strong overbought signal (consider selling).")
    elif latest_data['RSI'] < 30:
        print("  - 📉 Strong oversold signal (consider buying).")
    else:
        print("  - ⚖️ No strong signal detected.")
    
    if latest_data['EMA'] > latest_data['SMA']:
        print("  - 📈 EMA is above SMA, suggesting a bullish signal.")
    elif latest_data['EMA'] < latest_data['SMA']:
        print("  - 📉 EMA is below SMA, suggesting a bearish signal.")
    
    print("\n📅 Data range:", start_date, "to", end_date)
    print("📈 Happy Trading!\n")
    
    # Plot data
    plt.figure(figsize=(10, 5))
    plt.plot(df["Close"], label="Close Price", color="blue")
    plt.plot(df["SMA"], label=f"{sma_window}-day SMA", color="red", linestyle="dashed")
    plt.plot(df["EMA"], label=f"{ema_window}-day EMA", color="green", linestyle="dotted")
    plt.legend()
    plt.title(f"{ticker} Stock Price with Indicators")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.show()

import os

if os.getenv("RENDER"):
    # Use environment variables in Render
    ticker = os.getenv("TICKER", "AAPL")  
    start_date = os.getenv("START_DATE", "2024-01-01")  
    end_date = os.getenv("END_DATE", "2024-12-31")
else:
    # Allow user input locally
    ticker = input("Enter stock ticker: ").strip().upper() or "AAPL"
    start_date = input("Enter start date (YYYY-MM-DD): ").strip() or "2024-01-01"
    end_date = input("Enter end date (YYYY-MM-DD): ").strip() or "2024-12-31"

print("Using stock ticker:", ticker)
print("Start date:", start_date)
print("End date:", end_date)

