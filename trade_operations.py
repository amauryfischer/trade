import sqlite3
import yfinance as yf
from datetime import datetime
from termcolor import colored
from prettytable import PrettyTable
import pdb

companies = [
    {'ticker': 'BTC-EUR', 'color': 'yellow'},
    {'ticker': 'ETH-EUR', 'color': 'light_magenta'},
    {'ticker': 'SOL-EUR', 'color': 'light_cyan'},
    {'ticker': 'LTC-EUR', 'color': 'light_yellow'},
]

class TradeOperations:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cur = self.conn.cursor()
        self.cur.execute('''CREATE TABLE IF NOT EXISTS portfolio (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            ticker TEXT, 
                            quantity INTEGER,
                            bought_price REAL,
                            stop_loss REAL,
                            take_profit REAL,
                            leverage REAL)''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS budget (
                            id INTEGER PRIMARY KEY, 
                            amount REAL)''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS transactions (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            ticker TEXT,
                            quantity INTEGER,
                            price REAL,
                            transaction_type TEXT,
                            timestamp TEXT,
                            leverage REAL)''')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS short_positions (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            ticker TEXT, 
                            quantity INTEGER,
                            leverage REAL,
                            stop_loss REAL,
                            take_profit REAL)''')
        self.conn.commit()
        
        # Initialize budget if empty
        self.cur.execute('''SELECT amount FROM budget WHERE id=1''')
        if self.cur.fetchone() is None:
            self.cur.execute('''INSERT INTO budget (id, amount) VALUES (1, 100000)''')
            self.conn.commit()

    def buy(self, ticker, quantity, stop_loss, take_profit, leverage):
        stock = yf.Ticker(ticker).history(period='1d', interval='1m')
        price = stock['Close'].iloc[-1]
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        self.cur.execute('''SELECT amount FROM budget WHERE id=1''')
        budget = self.cur.fetchone()[0]

        total_cost = price * quantity
        if total_cost <= budget:
            budget -= total_cost
            self.cur.execute('''UPDATE budget SET amount=? WHERE id=1''', (budget,))
            
            self.cur.execute('''INSERT INTO portfolio 
                                (ticker, quantity, bought_price, stop_loss, take_profit, leverage) 
                                VALUES (?, ?, ?, ?, ?, ?)''', (ticker, quantity, price, stop_loss, take_profit, leverage))
            
            # Record the transaction
            self.cur.execute('''INSERT INTO transactions 
                                (ticker, quantity, price, transaction_type, timestamp, leverage) 
                                VALUES (?, ?, ?, 'buy', ?, ?)''', (ticker, quantity, price, timestamp, leverage))
            self.conn.commit()
            print(colored(f"Bought {quantity} shares of {ticker} at {price} each on {timestamp}. Remaining budget: ${budget}.", 'light_green'))

        else:
            print("Insufficient funds for this purchase.")

    def sell(self, ticker, quantity):
        self.cur.execute('''SELECT quantity, leverage, bought_price FROM portfolio WHERE ticker=? AND quantity=?''', (ticker, quantity))
        result = self.cur.fetchone()

        if result and result[0] >= quantity:
            stock = yf.Ticker(ticker).history(period='1d', interval='1m')
            price = stock['Close'].iloc[-1]
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            leverage = result[1]
            bought_price = result[2]

            gain = (price - bought_price) * quantity * leverage
            total_revenue = bought_price * quantity + gain
            self.cur.execute('''UPDATE portfolio SET quantity=quantity - ? WHERE ticker=? AND quantity=?''', (quantity, ticker, quantity))
            self.cur.execute('''DELETE FROM portfolio WHERE quantity=0''')
            
            self.cur.execute('''UPDATE budget SET amount=amount + ? WHERE id=1''', (total_revenue,))
            
            # Record the transaction
            self.cur.execute('''INSERT INTO transactions 
                                (ticker, quantity, price, transaction_type, timestamp, leverage) 
                                VALUES (?, ?, ?, 'sell', ?, ?)''', (ticker, quantity, price, timestamp, leverage))
            self.conn.commit()

            print(colored(f"Sold {quantity} shares of {ticker} at {price} on {timestamp}. Revenue: ${total_revenue}. Budget: ${self.cur.execute('''SELECT amount FROM budget WHERE id=1''').fetchone()[0]}.", 'light_red'))

        else:
            print("Not enough shares to sell.")
    
    def sell_short(self, ticker, quantity, leverage, stop_loss, take_profit):
        stock = yf.Ticker(ticker).history(period='1d', interval='1m')
        price = stock['Close'].iloc[-1]
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        total_revenue = price * quantity

        # Invert stop_loss and take_profit for short positions
        short_stop_loss = price * (1 + stop_loss)
        short_take_profit = price * (1 - take_profit)

        # Record the transaction
        self.cur.execute('''INSERT INTO transactions 
                            (ticker, quantity, price, transaction_type, timestamp, leverage) 
                            VALUES (?, ?, ?, 'short', ?, ?)''', (ticker, quantity, price, timestamp, leverage))
        
        self.cur.execute('''UPDATE budget SET amount=amount - ? WHERE id=1''', (total_revenue,))
        
        self.conn.commit()
        
        self.cur.execute('''INSERT INTO short_positions 
                            (ticker, quantity, leverage, stop_loss, take_profit) 
                            VALUES (?, ?, ?, ?, ?)''', (ticker, quantity, leverage, short_stop_loss, short_take_profit))

        self.conn.commit()
        print(colored(f"Shorted {quantity} shares of {ticker} at {price} each on {timestamp}. Remaining budget: ${self.cur.execute('''SELECT amount FROM budget WHERE id=1''').fetchone()[0]}.", 'light_red'))

    def buy_short(self, ticker, quantity):
        self.cur.execute('''SELECT quantity, leverage FROM short_positions WHERE ticker=? AND quantity=?''', (ticker, quantity))
        result = self.cur.fetchone()

        if result and result[0] >= quantity:
            stock = yf.Ticker(ticker).history(period='1d', interval='1m')
            price = stock['Close'].iloc[-1]
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            leverage = result[1]

            # Get the initial short price from transactions
            sold_price = self.cur.execute('''SELECT price FROM transactions WHERE ticker=? AND transaction_type='short' AND quantity=? ORDER BY timestamp DESC LIMIT 1''', (ticker, quantity)).fetchone()[0]
            gain = (sold_price - price) * quantity * leverage
            total_cost = sold_price * quantity + gain
            self.cur.execute('''UPDATE budget SET amount=amount + ? WHERE id=1''', (total_cost,))
            self.cur.execute('''UPDATE short_positions SET quantity=quantity - ? WHERE ticker=? AND quantity=?''', (quantity, ticker, quantity))
            self.cur.execute('''DELETE FROM short_positions WHERE quantity=0''')
            
            # Record the transaction
            self.cur.execute('''INSERT INTO transactions 
                                (ticker, quantity, price, transaction_type, timestamp, leverage) 
                                VALUES (?, ?, ?, 'buy_short', ?, ?)''', (ticker, quantity, price, timestamp, leverage))
            self.conn.commit()

            print(colored(f"Bought to cover {quantity} shares of {ticker} at {price} on {timestamp}. Total cost: ${total_cost}. Budget: ${self.cur.execute('''SELECT amount FROM budget WHERE id=1''').fetchone()[0]}.", 'light_red'))

        else:
            print("Not enough shares to cover.")

    def get_budget(self):
        self.cur.execute('''SELECT amount FROM budget WHERE id=1''')
        return self.cur.fetchone()[0]
    
    def print_portfolio(self):
        self.cur.execute('''SELECT * FROM portfolio''')
        portfolio = self.cur.fetchall()
        self.cur.execute('''SELECT * FROM short_positions''')
        short_positions = self.cur.fetchall()

        # Create tables
        table_portfolio = PrettyTable()
        table_short_positions = PrettyTable()

        table_portfolio.field_names = ["Ticker", "Quantity", "Bought Price", "Current Price", "Gain", "Stop-Loss", "Take-Profit", "Leverage"]
        table_short_positions.field_names = ["Ticker", "Quantity", "Shorted Price", "Current Price", "Gain", "Stop-Loss", "Take-Profit", "Leverage"]

        for id, ticker, quantity, bought_price, stop_loss, take_profit, leverage in portfolio:
            concerned_color = next((item['color'] for item in companies if item['ticker'] == ticker), 'white')
            current_price = self.get_current_price_one_unit(ticker)
            gain = (current_price - bought_price) * quantity * leverage
            table_portfolio.add_row([colored(ticker, concerned_color), quantity, bought_price, current_price, gain, stop_loss, take_profit, leverage])

        for id, ticker, quantity, leverage, stop_loss, take_profit in short_positions:
            concerned_color = next((item['color'] for item in companies if item['ticker'] == ticker), 'white')
            current_price = self.get_current_price_one_unit(ticker)
            sold_price = self.cur.execute('''SELECT price FROM transactions WHERE ticker=? AND transaction_type='short' AND quantity=? ORDER BY timestamp DESC LIMIT 1''', (ticker, quantity)).fetchone()[0]
            gain = (sold_price - current_price) * quantity * leverage
            table_short_positions.add_row([colored(ticker, concerned_color), quantity, sold_price, current_price, gain, stop_loss, take_profit, leverage])

        print(colored("Portfolio:", 'cyan', attrs=['bold']))
        print(table_portfolio)
        print(colored("Short Positions:", 'red', attrs=['bold']))
        print(table_short_positions)

    def check_portfolio_for_take_profit_or_stop_loss(self):
        self.cur.execute('''SELECT * FROM portfolio''')
        portfolio = self.cur.fetchall()
        self.cur.execute('''SELECT * FROM short_positions''')
        short_positions = self.cur.fetchall()

        for id, ticker, quantity, bought_price, stop_loss, take_profit, leverage in portfolio:
            current_price = self.get_current_price_one_unit(ticker)
            if current_price >= take_profit or current_price <= stop_loss:
                gain = (current_price - bought_price) * quantity * leverage
                gain_percentage = (gain / (bought_price * quantity * leverage)) * 100
                print(f"Conditions met for {ticker}: Current price {current_price:.2f}, Stop Loss {stop_loss:.2f}, Take Profit {take_profit:.2f}. Selling {quantity} shares.")
                print(colored(f"Gain: {gain:.2f} ({gain_percentage:.2f}%) with Leverage: {leverage}", 'green' if gain > 0 else 'red'))
                self.sell(ticker, quantity)

        for id, ticker, quantity, leverage, stop_loss, take_profit in short_positions:
            current_price = self.get_current_price_one_unit(ticker)
            sold_price = self.cur.execute('''SELECT price FROM transactions WHERE ticker=? AND transaction_type='short' AND quantity=? ORDER BY timestamp DESC LIMIT 1''', (ticker, quantity)).fetchone()[0]
            if current_price <= take_profit or current_price >= stop_loss:
                gain = (sold_price - current_price) * quantity * leverage
                gain_percentage = (gain / (sold_price * quantity * leverage)) * 100
                print(f"Conditions met for {ticker} (short): Current price {current_price:.2f}, Stop Loss {stop_loss:.2f}, Take Profit {take_profit:.2f}. Buying to cover {quantity} shares.")
                print(colored(f"Gain: {gain:.2f} ({gain_percentage:.2f}%) with Leverage: {leverage}", 'green' if gain > 0 else 'red'))
                self.buy_short(ticker, quantity)

    def sell_full_ticker(self, ticker):
        self.cur.execute('''SELECT quantity FROM portfolio WHERE ticker=?''', (ticker,))
        quantity = self.cur.fetchone()[0]
        self.sell(ticker, quantity)
    
    def sell_everything(self):
        self.cur.execute('''SELECT * FROM portfolio''')
        portfolio = self.cur.fetchall()
        for id, ticker, quantity, _, _, _, _ in portfolio:
            self.sell(ticker, quantity)
        self.cur.execute('''SELECT * FROM short_positions''')
        short_positions = self.cur.fetchall()
        for id, ticker, quantity, _, _, _ in short_positions:
            self.buy_short(ticker, quantity)
    
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
        self.cur.execute('''SELECT ticker, quantity, bought_price, leverage FROM portfolio''')
        portfolio = self.cur.fetchall()

        # Fetch all tickers and quantities from the short positions
        self.cur.execute('''SELECT ticker, quantity, leverage, stop_loss, take_profit FROM short_positions''')
        short_positions = self.cur.fetchall()

        total_value = budget
        for ticker, quantity, bought_price, leverage in portfolio:
            # Fetch the current price of each ticker
            stock = yf.Ticker(ticker).history(period='1d', interval='1m')
            price = stock['Close'].iloc[-1]

            # Calculate the gain and add it to the total value
            gain = (price - bought_price) * quantity
            total_value += bought_price * quantity + leverage * gain

        for ticker, quantity, leverage, stop_loss, take_profit in short_positions:
            # Fetch the current price of each ticker
            stock = yf.Ticker(ticker).history(period='1d', interval='1m')
            price = stock['Close'].iloc[-1]

            # Get the initial short price from transactions
            sold_price = self.cur.execute('''SELECT price FROM transactions WHERE ticker=? AND transaction_type='short' ORDER BY timestamp DESC LIMIT 1''', (ticker,)).fetchone()[0]
            gain = (sold_price - price) * quantity
            total_value += leverage * gain + sold_price * quantity

        print(f"Total portfolio value plus budget: " + colored(total_value, 'cyan', attrs=['bold']))
        return total_value
    
    def get_current_price_one_unit(self, ticker):
        stock = yf.Ticker(ticker).history(period='1d', interval='1m')
        return stock['Close'].iloc[-1]

    def __del__(self):
        self.conn.close()
