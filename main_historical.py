from backtesting import Backtesting
# Example usage
companies = [
    {'ticker': 'BTC-USD', 'color': 'yellow'},
    {'ticker': 'ETH-USD', 'color': 'yellow'},
    # Add other companies as needed
]

backtester = Backtesting(companies, '2020-01-01', '2021-01-02', 10000)
backtester.run_backtest()
