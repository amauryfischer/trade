import time
from termcolor import colored
from trade_operations import TradeOperations
from strategist import Strategist
from prettytable import PrettyTable

# Replace 'your_db_path.db' with the actual path to your SQLite database file
operations = TradeOperations('./your_db_path.db')

companies = [
    {'ticker': 'BTC-EUR', 'color': 'yellow'},
    {'ticker': 'ETH-EUR', 'color': 'light_magenta'},
    {'ticker': 'SOL-EUR', 'color': 'light_cyan'},
    # {'ticker': 'TSLA', 'color': 'light_green'}
]

def print_header():
    print("="*60)
    print(colored("Trading Bot", 'blue', attrs=['bold', 'underline']))
    print("="*60)

def print_footer():
    print("="*60)
    print(colored("End of Cycle", 'blue', attrs=['bold']))
    print("="*60)

while True:
    print_header()
    operations.calculate_total_value()
    # Check current portfolio and take necessary actions
    operations.check_portfolio_for_take_profit_or_stop_loss()

    for company in companies:
        ticker = company['ticker']
        print(f"========= " + colored(ticker, company['color'], attrs=['bold']) + " =========")
        
        strategist = Strategist(ticker, 'short')
        score = strategist.advice()
        strategist.generate_pdf_report(score)  # Pass the score to the PDF generation method

        price_one_unit = operations.get_current_price_one_unit(ticker)
        budget = operations.get_budget()
        stop_loss = 0.002  # 0.2% stop loss
        take_profit = 0.005  # 0.5% take profit

        if score > 90:
            leverage = 3
            quantity = budget * 0.08 / price_one_unit  # Larger position for very strong signals
            print(colored(f"Very Strong Buy for {ticker}", 'green', attrs=['bold']))
            operations.buy(ticker, quantity, price_one_unit * (1 - stop_loss), price_one_unit * (1 + take_profit), leverage)
        elif score > 80:
            leverage = 2
            quantity = budget * 0.05 / price_one_unit
            print(colored(f"Strong Buy for {ticker}", 'green', attrs=['bold']))
            operations.buy(ticker, quantity, price_one_unit * (1 - stop_loss), price_one_unit * (1 + take_profit), leverage)
        elif score > 60:
            leverage = 1
            quantity = budget * 0.02 / price_one_unit
            print(colored(f"Buy for {ticker}", 'green'))
            operations.buy(ticker, quantity, price_one_unit * (1 - stop_loss), price_one_unit * (1 + take_profit), leverage)
        elif score < 10:
            leverage = 3
            quantity = budget * 0.08 / price_one_unit  # Larger position for very strong signals
            print(colored(f"Very Strong Sell for {ticker}", 'red', attrs=['bold']))
            operations.sell_short(ticker, quantity, leverage, stop_loss, take_profit)
        elif score < 20:
            leverage = 2
            quantity = budget * 0.05 / price_one_unit
            print(colored(f"Strong Sell for {ticker}", 'red', attrs=['bold']))
            operations.sell_short(ticker, quantity, leverage, stop_loss, take_profit)
        elif score < 40:
            leverage = 1
            quantity = budget * 0.02 / price_one_unit
            print(colored(f"Sell for {ticker}", 'red'))
            operations.sell_short(ticker, quantity, leverage, stop_loss, take_profit)
        else:
            print(colored(f"Hold for {ticker}", 'yellow'))

    operations.calculate_total_value()
    operations.print_portfolio()
    print_footer()
    time.sleep(60)
