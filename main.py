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
    {'ticker': 'LTC-EUR', 'color': 'light_yellow'},
    {'ticker': 'TSLA', 'color': 'light_green'}
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
        advice, confidence = strategist.advice()
        strategist.generate_pdf_report(advice)  # Pass the general advice to the PDF generation method
        
        price_one_unit = operations.get_current_price_one_unit(ticker)
        budget = operations.get_budget()
        leverage = 3 if advice in ["Strong Buy", "Strong Sell"] else 1
        stop_loss = 0.002  # 0.2% stop loss
        take_profit = 0.005  # 0.5% take profit

        if advice == "Strong Buy":
            print(colored(f"Strong Buy for {ticker}", 'green', attrs=['bold']))
            quantity = budget * 0.04 / price_one_unit  # Leverage should not affect quantity
            operations.buy(ticker, quantity, price_one_unit * (1 - stop_loss), price_one_unit * (1 + take_profit), leverage)
        elif advice == "Buy":
            quantity = budget * 0.01 / price_one_unit  # Leverage should not affect quantity
            operations.buy(ticker, quantity, price_one_unit * (1 - stop_loss), price_one_unit * (1 + take_profit), leverage)
        elif advice in ["Sell", "Strong Sell"]:
            print(colored(f"{advice} for {ticker}", 'red', attrs=['bold']))
            quantity = budget * 0.04 / price_one_unit  # Leverage should not affect quantity
            operations.sell_short(ticker, quantity, leverage, stop_loss, take_profit)

    operations.calculate_total_value()
    operations.print_portfolio()
    print_footer()
    time.sleep(60)
