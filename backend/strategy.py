import yfinance as yf
import numpy as np
import pandas as pd
from schemas import BacktestResponse


def run_backtest(ticker: str, fast_ma: int, slow_ma: int) -> BacktestResponse:
    # 1. Fetch Data (The "Input")
    # We fetch 5 years of data to ensure we have enough history for the Slow MA
    data = yf.download(ticker, period="5y", interval="1d", progress=False)

    if data.empty:
        return BacktestResponse(total_return="0.0%", sharpe_ratio=0.0)

    # 2. Calculate Indicators (The "Processing")
    # We use Pandas to calculate the averages instantly
    data["fast_ma"] = data["Close"].rolling(window=fast_ma).mean()
    data["slow_ma"] = data["Close"].rolling(window=slow_ma).mean()

    # 3. Define the Signal (The "Logic")
    # If Fast > Slow, we want to be in the market (1). Otherwise, out (0).
    data["signal"] = np.where(data["fast_ma"] > data["slow_ma"], 1, 0)

    # 4. Calculate Returns (The "Result")
    # 'pct_change' is the daily return of the stock.
    data["Stock_Return"] = data["Close"].pct_change()

    # We shift the signal by 1 day because we can only trade TOMORROW based on TODAY's signal.
    # (Avoiding "Lookahead Bias" - a common rookie mistake)
    data["Strategy_Return"] = data["signal"].shift(1) * data["Stock_Return"]

    # Drop NaN values before calculations
    data = data.dropna()

    # 5. Calculate Metrics (The "Output")
    # Total Return: Compounding the daily returns
    cumulative_return = (1 + data["Strategy_Return"]).cumprod() - 1
    total_return_pct = cumulative_return.iloc[-1] * 100

    # Sharpe Ratio: Annualized Mean / Annualized Std Dev
    # (Assuming 252 trading days in a year)
    daily_mean = data["Strategy_Return"].mean()
    daily_std = data["Strategy_Return"].std()

    if daily_std == 0:
        sharpe = 0.0
    else:
        sharpe = (daily_mean / daily_std) * (252**0.5)

    return BacktestResponse(
        total_return=f"{total_return_pct:.2f}%",
        sharpe_ratio=round(sharpe, 2),
    )
