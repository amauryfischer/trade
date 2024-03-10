from trade_operations import TradeOperations
from strategist import Strategist
import time
from termcolor import colored

# Remplacez 'your_db_path.db' par le chemin d'accès à votre fichier de base de données SQLite
operations = TradeOperations('your_db_path.db')

while True:
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
    for company in companies:
        print(f"=========Short " + colored(company['ticker'], company['color']) + "=========")
        StrategyShort = Strategist(company['ticker'], 'short')
        advice_short = StrategyShort.advice()
        #StrategyShort.generate_pdf_report()
        price_one_unit = operations.get_current_price_one_unit(company['ticker'])
        budget = operations.get_budget()

        if advice_short == "Strong Buy":
            # invest 4% of the budget for strong buy advice
            quantity = float(budget * 0.04 / price_one_unit)
            operations.buy(company['ticker'], quantity)
        elif advice_short == "Buy":
            # invest 1% of the budget for buy advice
            quantity = float(budget * 0.01 / price_one_unit)
            operations.buy(company['ticker'], quantity)
        elif advice_short == "Sell":
            # sell a portion or specific strategy for selling
            operations.sell_specific(company['ticker'])
        elif advice_short == "Strong Sell":
            # sell everything related to that ticker
            operations.sell_everything(company['ticker'])
        # No specific action for 'Hold' or other advice categories

    operations.calculate_total_value()
    operations.print_portfolio()
    time.sleep(60)