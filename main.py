import time
from termcolor import colored
from trade_operations import TradeOperations
from strategist import Strategist

# Remplacez 'your_db_path.db' par le chemin d'accès à votre fichier de base de données SQLite
operations = TradeOperations('your_db_path.db')

companies = [
    {'ticker': 'BTC-USD', 'color': 'yellow'},
    {'ticker': 'ETH-USD', 'color': 'yellow'},
    {'ticker': 'BNB-USD', 'color': 'yellow'},
    {'ticker': 'XRP-USD', 'color': 'yellow'},
    {'ticker': 'ADA-USD', 'color': 'yellow'},
    {'ticker': 'SOL-USD', 'color': 'yellow'},
    {'ticker': 'DOT-USD', 'color': 'yellow'},
    {'ticker': 'DOGE-USD', 'color': 'yellow'},
    {'ticker': 'AVAX-USD', 'color': 'yellow'},
    {'ticker': 'LTC-USD', 'color': 'yellow'},
    {'ticker': 'LINK-USD', 'color': 'yellow'},
    {'ticker': 'MATIC-USD', 'color': 'yellow'}
]

while True:
    for company in companies:
        ticker = company['ticker']
        print(f"========= Short " + colored(ticker, company['color']) + " =========")
        
        strategist = Strategist(ticker, 'short')
        advice = strategist.advice()
        price_one_unit = operations.get_current_price_one_unit(ticker)
        budget = operations.get_budget()

        if advice == "Strong Buy":
            quantity = budget * 0.04 / price_one_unit
            operations.buy(ticker, quantity)
        elif advice == "Buy":
            quantity = budget * 0.01 / price_one_unit
            operations.buy(ticker, quantity)
        elif advice == "Sell":
            operations.sell_specific(ticker)
        elif advice == "Strong Sell":
            operations.sell_everything(ticker)

    operations.calculate_total_value()
    operations.print_portfolio()
    time.sleep(60)
