import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import os
from termcolor import colored

class Strategist:
    def __init__(self, ticker, term='short'):
        self.term = term
        self.ticker = ticker
        # Définition des paramètres en fonction du terme
        if term == 'short':
            self.period = '1d'
            self.interval = '1m'
            self.short_window = 5
            self.long_window = 20
            self.rsi_window = 14
            self.macd_short = 12
            self.macd_long = 26
            self.macd_signal = 9
        elif term == 'medium':
            self.period = '1mo'
            self.interval = '1h'
            self.short_window = 12
            self.long_window = 26
            self.rsi_window = 14
            self.macd_short = 12
            self.macd_long = 26
            self.macd_signal = 9
        elif term == 'long':
            self.period = '1y'
            self.interval = '1d'
            self.short_window = 50
            self.long_window = 200
            self.rsi_window = 14
            self.macd_short = 12
            self.macd_long = 26
            self.macd_signal = 9
        else:
            raise ValueError("Term must be 'short', 'medium', or 'long'")
        
        # Récupération des données
        self.data = yf.Ticker(ticker).history(period=self.period, interval=self.interval)
        

    def moving_average_crossover(self):
        # Utilize the class' short_window and long_window attributes
        signals = pd.DataFrame(index=self.data.index)
        signals['signal'] = 0.0
        signals['short_mavg'] = self.data['Close'].rolling(window=self.short_window, min_periods=1, center=False).mean()
        signals['long_mavg'] = self.data['Close'].rolling(window=self.long_window, min_periods=1, center=False).mean()
        
        signals['signal'][self.short_window:] = np.where(signals['short_mavg'][self.short_window:] 
                                                    > signals['long_mavg'][self.short_window:], 1.0, 0.0)   
        signals['positions'] = signals['signal'].diff()

        self.data['short_mavg'] = signals['short_mavg']
        self.data['long_mavg'] = signals['long_mavg']
        self.data['positions'] = signals['positions']
        

    def relative_strength_index(self):
        window_length = self.rsi_window  # Use the class' rsi_window attribute
        close = self.data['Close']
        
        delta = close.diff()
        delta = delta[1:] 

        up, down = delta.copy(), delta.copy()
        up[up < 0] = 0
        down[down > 0] = 0

        roll_up = up.rolling(window_length).mean()
        roll_down = down.abs().rolling(window_length).mean()

        RS = roll_up / roll_down
        RSI = 100.0 - (100.0 / (1.0 + RS))

        self.data['RSI'] = RSI
    
    def macd(self):
        exp1 = self.data['Close'].ewm(span=self.macd_short, adjust=False).mean()
        exp2 = self.data['Close'].ewm(span=self.macd_long, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=self.macd_signal, adjust=False).mean()

        self.data['MACD'] = macd
        self.data['Signal Line'] = signal


    def plot(self, strategy_name, data):
        if strategy_name == 'Moving Average Crossover':
            plt.plot(data.index, data['Close'], label='Close Price')
            plt.plot(data.index, data['short_mavg'], label=f'{self.short_window}-Day Moving Average')
            plt.plot(data.index, data['long_mavg'], label=f'{self.long_window}-Day Moving Average')

            # Find indices where buy signals occur and plot
            buy_signals = data.loc[data['positions'] == 1]
            plt.plot(buy_signals.index, data['Close'][buy_signals.index], '^', markersize=10, label='Buy Signal', color='g')

            # Find indices where sell signals occur and plot
            sell_signals = data.loc[data['positions'] == -1]
            plt.plot(sell_signals.index, data['Close'][sell_signals.index], 'v', markersize=10, label='Sell Signal', color='r')

        elif strategy_name == 'RSI':
            plt.subplot(2, 1, 1)
            plt.plot(data.index, data['Close'], label='Close Price')
            plt.legend()
            plt.title(f'Close Price for {self.ticker}')
            
            plt.subplot(2, 1, 2)
            plt.plot(data.index, data['RSI'], label='RSI', color='purple')
            plt.axhline(70, linestyle='--', alpha=0.5, color='red')
            plt.axhline(30, linestyle='--', alpha=0.5, color='green')
            plt.ylim(0, 100)  # Adjust Y-axis to focus on RSI scale
            plt.legend()
            plt.title(f'RSI for {self.ticker}')
        elif strategy_name == 'MACD':
            plt.plot(data.index, data['MACD'], label='MACD', color='blue')
            plt.plot(data.index, data['Signal Line'], label='Signal Line', color='red')
        
        plt.tight_layout()  # Adjust layout to make room for all plots
        plt.legend()
        plt.title(f'{strategy_name} for {self.ticker}')



    def generate_pdf_report(self):
        # Ensure the directory for self.ticker exists
        directory = self.ticker
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        # Create the PDF report within the specified directory and using self.term in the filename
        pdf_path = f'{directory}/{self.ticker}_strategy_report_{self.term}.pdf'
        with PdfPages(pdf_path) as pdf:
            for strategy_method in [self.relative_strength_index, self.macd, self.moving_average_crossover]:
                plt.figure(figsize=(10, 5))
                strategy_method()
                self.plot(strategy_method.__name__, self.data)
                pdf.savefig()  # saves the current figure into a pdf page
                plt.close()
    
    def advice(self):
        self.relative_strength_index()
        self.macd()
        self.moving_average_crossover()
        
        advice_details = []
        
        # Moving Average Crossover Advice
        mac_signals = self.data['short_mavg'] > self.data['long_mavg']
        if mac_signals.iloc[-1] and not mac_signals.iloc[-2]:
            mac_advice = 'Buy'
            advice_details.append('Moving Average Crossover suggests '+colored("Buy",'green')+' as the short moving average crossed above the long moving average.')
        elif not mac_signals.iloc[-1] and mac_signals.iloc[-2]:
            mac_advice = 'Sell'
            advice_details.append('Moving Average Crossover suggests '+colored('Sell','red')+' as the short moving average crossed below the long moving average.')
        else:
            mac_advice = 'Hold'
            advice_details.append('Moving Average Crossover suggests '+colored('Hold','magenta')+' as there is no recent crossover between the short and long moving averages.')

        # RSI Advice
        current_RSI = self.data['RSI'].iloc[-1]
        if current_RSI < 30:
            rsi_advice = 'Buy'
            advice_details.append('RSI suggests ' + colored("Buy",'green') +' as it is below 30, indicating the stock might be oversold.')
        elif current_RSI > 70:
            rsi_advice = 'Sell'
            advice_details.append('RSI suggests' + colored('Sell','red')+ ' as it is above 70, indicating the stock might be overbought.')
        else:
            rsi_advice = 'Hold'
            advice_details.append('RSI suggests '+colored('Hold','magenta')+' as it is between 30 and 70, indicating no extreme conditions.')

        # MACD Advice
        macd_cross = self.data['MACD'].iloc[-1] > self.data['Signal Line'].iloc[-1]
        if macd_cross and not (self.data['MACD'].iloc[-2] > self.data['Signal Line'].iloc[-2]):
            macd_advice = 'Buy'
            advice_details.append('MACD suggests '+colored('Buy','green')+' as the MACD line crossed above the Signal line.')
        elif not macd_cross and (self.data['MACD'].iloc[-2] > self.data['Signal Line'].iloc[-2]):
            macd_advice = 'Sell'
            advice_details.append('MACD suggests '+colored('Sell','red')+' as the MACD line crossed below the Signal line.')
        else:
            macd_advice = 'Hold'
            advice_details.append('MACD suggests '+colored('Hold','magenta')+' as there is no recent cross between the MACD and Signal lines.')

        # Aggregate advice
        advices = [mac_advice, rsi_advice, macd_advice]

        # Initialize scores
        buy_score = 0
        sell_score = 0

        # Define points for each advice
        advice_points = {
            'Strong Buy': 2,
            'Buy': 1,
            'Hold': 0,
            'Sell': -1,
            'Strong Sell': -2,
        }

        # Calculate scores
        for advice in advices:
            if advice in advice_points:
                score = advice_points[advice]
                if score > 0:
                    buy_score += score
                else:
                    sell_score += abs(score)

        # Determine final advice
        if buy_score >= 4:
            final_advice = 'Strong Buy'
        elif buy_score > sell_score:
            final_advice = 'Buy'
        elif sell_score >= 4:
            final_advice = 'Strong Sell'
        elif sell_score > buy_score:
            final_advice = 'Sell'
        else:
            final_advice = 'Hold'

        # Printing final advice along with detailed reasons
        # for detail in advice_details:
        #     print(detail)
        color_final_advice = 'green' if final_advice in ['Strong Buy', 'Buy'] else 'red' if final_advice in ['Strong Sell', 'Sell'] else 'magenta'
        print("---Final advice for " + colored(self.ticker,'yellow') + " " + colored(final_advice,color_final_advice) + '---')

        return final_advice

