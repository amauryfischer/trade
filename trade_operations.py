import sqlite3
import yfinance as yf
from datetime import datetime
from termcolor import colored

class TradeOperations:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cur = self.conn.cursor()
        self.cur.execute('''CREATE TABLE IF NOT EXISTS portfolio (
                            ticker TEXT PRIMARY KEY, 
                            quantity INTEGER)''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS budget (
                            id INTEGER PRIMARY KEY, 
                            amount REAL)''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS transactions (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            ticker TEXT,
                            quantity INTEGER,
                            price REAL,
                            transaction_type TEXT,
                            timestamp TEXT)''')
        self.conn.commit()
        
        # Initialize budget if empty
        self.cur.execute('''SELECT amount FROM budget WHERE id=1''')
        if self.cur.fetchone() is None:
            self.cur.execute('''INSERT INTO budget (id, amount) VALUES (1, 100000)''')
            self.conn.commit()

    def buy(self, ticker, quantity):
        stock = yf.Ticker(ticker).history(period='1d', interval='1m')
        price = stock['Close'].iloc[-1]
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        self.cur.execute('''SELECT amount FROM budget WHERE id=1''')
        budget = self.cur.fetchone()[0]

        total_cost = price * quantity
        if total_cost <= budget:
            budget -= total_cost
            self.cur.execute('''UPDATE budget SET amount=? WHERE id=1''', (budget,))
            
            self.cur.execute('''SELECT quantity FROM portfolio WHERE ticker=?''', (ticker,))
            result = self.cur.fetchone()
            if result:
                self.cur.execute('''UPDATE portfolio SET quantity=quantity + ? WHERE ticker=?''', (quantity, ticker))
            else:
                self.cur.execute('''INSERT INTO portfolio (ticker, quantity) VALUES (?, ?)''', (ticker, quantity))
            
            # Record the transaction
            self.cur.execute('''INSERT INTO transactions (ticker, quantity, price, transaction_type, timestamp) 
                                VALUES (?, ?, ?, 'buy', ?)''', (ticker, quantity, price, timestamp))
            self.conn.commit()
            print(colored(f"Bought {quantity} shares of {ticker} at {price} each on {timestamp}. Remaining budget: ${budget}.",'green'))

        else:
            print("Insufficient funds for this purchase.")

    def sell(self, ticker, quantity):
        self.cur.execute('''SELECT quantity FROM portfolio WHERE ticker=?''', (ticker,))
        result = self.cur.fetchone()

        if result and result[0] >= quantity:
            stock = yf.Ticker(ticker).history(period='1d', interval='1m')
            price = stock['Close'].iloc[-1]
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            total_revenue = price * quantity
            self.cur.execute('''UPDATE portfolio SET quantity=quantity - ? WHERE ticker=?''', (quantity, ticker))
            self.cur.execute('''UPDATE budget SET amount=amount + ? WHERE id=1''', (total_revenue,))
            
            # Record the transaction
            self.cur.execute('''INSERT INTO transactions (ticker, quantity, price, transaction_type, timestamp) 
                                VALUES (?, ?, ?, 'sell', ?)''', (ticker, quantity, price, timestamp))
            self.conn.commit()

            print(colored(f"Sold {quantity} shares of {ticker} at {price} on {timestamp}. Revenue: ${total_revenue}. Budget: ${self.cur.execute('''SELECT amount FROM budget WHERE id=1''').fetchone()[0]}.",'red'))

        else:
            print("Not enough shares to sell.")
    
    def get_budget(self):
        self.cur.execute('''SELECT amount FROM budget WHERE id=1''')
        return self.cur.fetchone()[0]
    
    def print_portfolio(self):
        self.cur.execute('''SELECT * FROM portfolio''')
        portfolio = self.cur.fetchall()
        print(colored("Portfolio:", 'cyan'))
        for ticker, quantity in portfolio:
            print(f"{ticker}: {quantity} shares")
    
    def sell_everything(self):
        self.cur.execute('''SELECT * FROM portfolio''')
        portfolio = self.cur.fetchall()
        for ticker, quantity in portfolio:
            self.sell(ticker, quantity)
    
    def sell_specific(self, ticker):
        self.cur.execute('''SELECT quantity FROM portfolio WHERE ticker=?''', (ticker,))
        result = self.cur.fetchone()
        if result:
            self.sell(ticker, result[0])
        else:
            print(f"No shares of {ticker} to sell.")
    
    def calculate_total_value(self):
        # Fetch the current budget
        self.cur.execute('''SELECT amount FROM budget WHERE id=1''')
        budget = self.cur.fetchone()[0]

        # Fetch all tickers and quantities from the portfolio
        self.cur.execute('''SELECT ticker, quantity FROM portfolio''')
        portfolio = self.cur.fetchall()

        total_value = budget
        for ticker, quantity in portfolio:
            # Fetch the current price of each ticker
            stock = yf.Ticker(ticker).history(period='1d', interval='1m')
            price = stock['Close'].iloc[-1]

            # Calculate the value of each position and add it to the total value
            total_value += price * quantity

        print(f"Total portfolio value plus budget: " + colored(total_value, 'cyan'))
        return total_value
    
    def get_current_price_one_unit(self, ticker):
        stock = yf.Ticker(ticker).history(period='1d', interval='1m')
        return stock['Close'].iloc[-1]


    def __del__(self):
        self.conn.close()
