import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import os
from termcolor import colored

class Strategist:
    def __init__(self, ticker, term='short'):
        self.ticker = ticker
        self.setup_term_parameters(term)
        self.data = yf.Ticker(ticker).history(period=self.period, interval=self.interval)

    def setup_term_parameters(self, term):
        terms = {
            'short': ('1d', '1m', 5, 20, 14, 12, 26, 9),
            'medium': ('1mo', '1h', 12, 26, 14, 12, 26, 9),
            'long': ('1y', '1d', 50, 200, 14, 12, 26, 9)
        }
        if term in terms:
            self.period, self.interval, self.short_window, self.long_window, self.rsi_window, self.macd_short, self.macd_long, self.macd_signal = terms[term]
        else:
            raise ValueError("Term must be 'short', 'medium', or 'long'")

    def calculate_indicators(self):
        self.calculate_moving_averages()
        self.calculate_rsi()
        self.calculate_macd()

    def calculate_moving_averages(self):
        self.data['short_mavg'] = self.data['Close'].rolling(window=self.short_window).mean()
        self.data['long_mavg'] = self.data['Close'].rolling(window=self.long_window).mean()
        self.data['positions'] = pd.Series(np.where(self.data['short_mavg'] > self.data['long_mavg'], 1, 0), index=self.data.index).diff().fillna(0)

    def calculate_rsi(self):
        delta = self.data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(self.rsi_window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(self.rsi_window).mean()
        rs = gain / loss
        self.data['RSI'] = 100 - (100 / (1 + rs))

    def calculate_macd(self):
        exp1 = self.data['Close'].ewm(span=self.macd_short, adjust=False).mean()
        exp2 = self.data['Close'].ewm(span=self.macd_long, adjust=False).mean()
        self.data['MACD'] = exp1 - exp2
        self.data['Signal Line'] = self.data['MACD'].ewm(span=self.macd_signal, adjust=False).mean()

    def advice(self):
        self.calculate_indicators()
        mac_advice = self.analyze_moving_averages()
        rsi_advice = self.analyze_rsi()
        macd_advice = self.analyze_macd()
        return self.aggregate_advice(mac_advice, rsi_advice, macd_advice)

    def analyze_moving_averages(self):
        latest_position = self.data['positions'].iloc[-1]
        if latest_position == 1:
            return 'Buy'
        elif latest_position == -1:
            return 'Sell'
        return 'Hold'

    def analyze_rsi(self):
        current_rsi = self.data['RSI'].iloc[-1]
        if current_rsi < 30:
            return 'Buy'
        elif current_rsi > 70:
            return 'Sell'
        return 'Hold'

    def analyze_macd(self):
        macd_above_signal = self.data['MACD'].iloc[-1] > self.data['Signal Line'].iloc[-1]
        macd_crossed_above = self.data['MACD'].iloc[-2] <= self.data['Signal Line'].iloc[-2]
        if macd_above_signal and macd_crossed_above:
            return 'Buy'
        elif not macd_above_signal and not macd_crossed_above:
            return 'Sell'
        return 'Hold'

    def aggregate_advice(self, mac_advice, rsi_advice, macd_advice):
        advice_map = {'Strong Buy': 2, 'Buy': 1, 'Hold': 0, 'Sell': -1, 'Strong Sell': -2}
        advice_scores = [advice_map[mac_advice], advice_map[rsi_advice], advice_map[macd_advice]]
        total_score = sum(advice_scores)

        if total_score >= 4:
            return 'Strong Buy'
        elif total_score >= 1:
            return 'Buy'
        elif total_score <= -4:
            return 'Strong Sell'
        elif total_score <= -1:
            return 'Sell'
        return 'Hold'

    def generate_pdf_report(self):
        os.makedirs(self.ticker, exist_ok=True)
        pdf_path = f'{self.ticker}/{self.ticker}_strategy_report_{self.term}.pdf'
        with PdfPages(pdf_path) as pdf:
            for strategy_method in [self.calculate_rsi, self.calculate_macd, self.calculate_moving_averages]:
                plt.figure(figsize=(10, 5))
                strategy_method()
                self.plot(strategy_method.__name__)
                pdf.savefig()
                plt.close()

    def plot(self, strategy_name):
        if strategy_name == 'calculate_moving_averages':
            plt.plot(self.data['Close'], label='Close Price')
            plt.plot(self.data['short_mavg'], label=f'{self.short_window}-Day MA')
            plt.plot(self.data['long_mavg'], label=f'{self.long_window}-Day MA')
            self.plot_signals()
        elif strategy_name == 'calculate_rsi':
            plt.subplot(2, 1, 1)
            plt.plot(self.data['Close'], label='Close Price')
            plt.legend()
            plt.title(f'Close Price for {self.ticker}')
            plt.subplot(2, 1, 2)
            plt.plot(self.data['RSI'], label='RSI', color='purple')
            plt.axhline(70, linestyle='--', color='red')
            plt.axhline(30, linestyle='--', color='green')
            plt.legend()
            plt.title(f'RSI for {self.ticker}')
        elif strategy_name == 'calculate_macd':
            plt.plot(self.data['MACD'], label='MACD', color='blue')
            plt.plot(self.data['Signal Line'], label='Signal Line', color='red')
            plt.legend()
        plt.tight_layout()

    def plot_signals(self):
        buy_signals = self.data[self.data['positions'] == 1]
        sell_signals = self.data[self.data['positions'] == -1]
        plt.plot(buy_signals.index, self.data['Close'][buy_signals.index], '^', markersize=10, color='g', label='Buy Signal')
        plt.plot(sell_signals.index, self.data['Close'][sell_signals.index], 'v', markersize=10, color='r', label='Sell Signal')
        plt.legend()
