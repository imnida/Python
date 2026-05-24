# Finance / Quant Skill

## Repo patterns
- Data sources: `yfinance` (primary), `pandas_datareader`
- Existing work: simple returns (`simple_returns.py`), portfolio optimization (`portfolio_optimization.py`), LSTM stock prediction (`LSTM_Stock/`), candlestick charts, Bitcoin price notifications
- SVM and regression-based stock prediction also present (`SVM_Stock/`, `Regression_Stock/`)

## Returns and statistics
- Distinguish simple returns vs log returns — state which is being used and why
- Annualize metrics explicitly: `* 252` for daily → annual, `* np.sqrt(252)` for vol
- Sharpe ratio: always state the risk-free rate used (even if 0)
- For cumulative performance: use a growth-of-$1 chart, not raw price

## Portfolio analysis
- State constraints upfront: long-only, sum-to-one, no leverage
- Report: expected return, volatility, Sharpe ratio for each portfolio on the efficient frontier
- Highlight the max Sharpe and min-variance portfolios specifically

## Backtesting discipline
- Always state: in-sample vs out-of-sample periods
- Flag look-ahead bias risks (e.g. using full-period mean for z-score normalization)
- Survivorship bias: note if using current index constituents to analyze historical performance

## Data hygiene
- Check for and handle corporate actions (splits, dividends) — `yfinance` `auto_adjust=True` by default
- Check for missing trading days and decide on fill strategy (forward-fill for prices, zero for returns)
- Always print the actual date range of data retrieved, not just the requested range
