import yfinance as yf
import pandas as pd

class Backtesting:
    def __init__(self, companies, start_date, end_date, initial_budget):
        self.companies = companies
        self.start_date = start_date
        self.end_date = end_date
        self.initial_budget = initial_budget
        self.portfolio = {company['ticker']: 0 for company in companies}  # Tracks quantity of each asset
        self.cash = initial_budget
        self.transaction_log = []

    def fetch_data(self, ticker):
        data = yf.download(ticker, start=self.start_date, end=self.end_date)
        return data

    def simulate_trades(self):
        for company in self.companies:
            data = self.fetch_data(company['ticker'])
            # Assume using close prices for simplicity
            closing_prices = data['Close']
            for date, price in closing_prices.iteritems():
                # Your existing strategy here, simplified for demonstration
                # Replace with your strategy's actual advice
                advice = 'Buy'  # Placeholder, replace with call to your strategy
                quantity = 0
                if advice == "Strong Buy":
                    quantity = self.cash * 0.04 / price
                elif advice == "Buy":
                    quantity = self.cash * 0.01 / price

                if quantity > 0:
                    self.buy(company['ticker'], quantity, price)
                # Similar logic for sell signals
                
                # Log the transaction
                self.transaction_log.append({
                    'date': date,
                    'ticker': company['ticker'],
                    'action': advice,
                    'quantity': quantity,
                    'price': price,
                    'value': quantity * price
                })

    def buy(self, ticker, quantity, price):
        self.portfolio[ticker] += quantity
        self.cash -= quantity * price

    def sell(self, ticker, quantity, price):
        if self.portfolio[ticker] >= quantity:
            self.portfolio[ticker] -= quantity
            self.cash += quantity * price

    def evaluate_performance(self):
        # Method to evaluate the portfolio's performance over time
        final_value = self.cash + sum(self.portfolio[ticker] * self.fetch_data(ticker)['Close'].iloc[-1] for ticker in self.portfolio)
        return final_value, final_value - self.initial_budget

    def run_backtest(self):
        self.simulate_trades()
        final_value, profit = self.evaluate_performance()
        print(f"Final Portfolio Value: {final_value}, Profit: {profit}")
        # Optionally, print or analyze transaction_log for detailed insights

