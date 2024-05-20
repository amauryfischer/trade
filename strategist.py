import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import pdb
import os


class Strategist:
    def __init__(self, ticker, term='short', pivot_type='Traditional', pivot_timeframe='daily'):
        self.ticker = ticker
        self.term = term
        self.pivot_type = pivot_type
        self.pivot_timeframe = pivot_timeframe
        self.setup_term_parameters(term)
        self.data = yf.Ticker(ticker).history(period=self.period, interval=self.interval)
        self.daily_data = yf.Ticker(ticker).history(period='1d', interval='1m')  # Fetch daily data for pivot points
        self.set_pivot_timeframe_data()

    def setup_term_parameters(self, term):
        terms = {
            'very_short': ('1d', '1m', 3, 10, 9, 3, 10, 5),
            'short': ('1d', '1m', 5, 20, 14, 12, 26, 9),
            'medium': ('1mo', '1h', 12, 26, 14, 12, 26, 9),
            'long': ('1y', '1d', 50, 200, 14, 12, 26, 9),
        }
        if term in terms:
            self.period, self.interval, self.short_window, self.long_window, self.rsi_window, self.macd_short, self.macd_long, self.macd_signal = terms[term]
        else:
            raise ValueError("Term must be 'very_short', 'short', 'medium', or 'long'")

    def set_pivot_timeframe_data(self):
        if self.pivot_timeframe == 'daily':
            self.pivot_data = self.daily_data
        elif self.pivot_timeframe == 'weekly':
            self.pivot_data = self.daily_data.resample('W').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'})
        elif self.pivot_timeframe == 'monthly':
            self.pivot_data = self.daily_data.resample('M').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'})
        else:
            raise ValueError("Pivot timeframe must be 'daily', 'weekly', or 'monthly'")

    def calculate_indicators(self):
        self.calculate_moving_averages()
        self.calculate_rsi()
        self.calculate_macd()
        self.calculate_bollinger_bands()
        self.calculate_stochastic_oscillator()
        self.calculate_pivot_points()  # Moved here for consistent calculation order

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

    def calculate_bollinger_bands(self):
        self.data['20_MA'] = self.data['Close'].rolling(window=20).mean()
        self.data['20_STD'] = self.data['Close'].rolling(window=20).std()
        self.data['Upper Band'] = self.data['20_MA'] + (self.data['20_STD'] * 2)
        self.data['Lower Band'] = self.data['20_MA'] - (self.data['20_STD'] * 2)

    def calculate_stochastic_oscillator(self):
        low_min = self.data['Low'].rolling(window=14).min()
        high_max = self.data['High'].rolling(window=14).max()
        self.data['%K'] = 100 * (self.data['Close'] - low_min) / (high_max - low_min)
        self.data['%D'] = self.data['%K'].rolling(window=3).mean()

    def calculate_pivot_points(self):
        max_value = self.pivot_data['High'].max()
        min_value = self.pivot_data['Low'].min()
        close = self.pivot_data['Close'][0]
        self.pivot_data['Pivot'] = (max_value + min_value + close) / 3
        self.pivot_data['R1'] = 2 * self.pivot_data['Pivot'] - min_value
        self.pivot_data['S1'] = 2 * self.pivot_data['Pivot'] - max_value
        self.pivot_data['R2'] = self.pivot_data['Pivot'] + (max_value - min_value)
        self.pivot_data['S2'] = self.pivot_data['Pivot'] - (max_value - min_value)
        self.pivot_data['R3'] = max_value + 2 * (self.pivot_data['Pivot'] - min_value)
        self.pivot_data['S3'] = min_value - 2 * (max_value - self.pivot_data['Pivot'])
        self.pivot_data['R2'] = self.pivot_data['Pivot'] + (max_value - min_value)
        self.pivot_data['S2'] = self.pivot_data['Pivot'] - (max_value - min_value)
        self.pivot_data['R3'] = max_value + 2 * (self.pivot_data['Pivot'] - min_value)
        self.pivot_data['S3'] = min_value - 2 * (max_value - self.pivot_data['Pivot'])


    def analyze_pivot_points(self):
        close = self.data['Close'].iloc[-1]
        pivot = self.pivot_data['Pivot'].iloc[-1]
        if close > pivot:
            return 'Buy', 'Price is above the Pivot Point'
        elif close < pivot:
            return 'Sell', 'Price is below the Pivot Point'
        return 'Hold', 'Price is around the Pivot Point'

    def advice(self):
        self.calculate_indicators()
        
        mac_advice = self.analyze_moving_averages()
        rsi_advice = self.analyze_rsi()
        macd_advice = self.analyze_macd()
        bollinger_advice = self.analyze_bollinger_bands()
        stochastic_advice = self.analyze_stochastic_oscillator()
        pivot_advice = self.analyze_pivot_points()
        
        final_advice, confidence = self.aggregate_advice(mac_advice, rsi_advice, macd_advice, bollinger_advice, stochastic_advice, pivot_advice)
        return final_advice, confidence

    def analyze_moving_averages(self):
        latest_position = self.data['positions'].iloc[-1]
        if latest_position == 1:
            return 'Buy', 'Short MA crossed above Long MA'
        elif latest_position == -1:
            return 'Sell', 'Short MA crossed below Long MA'
        return 'Hold', 'No significant crossover'

    def analyze_rsi(self):
        current_rsi = self.data['RSI'].iloc[-1]
        if current_rsi <= 10:
            print(f"\033[91mStrong Signal: RSI is {current_rsi} (<= 10)\033[0m")
        if current_rsi < 30:
            return 'Buy', 'RSI is below 30'
        elif current_rsi > 70:
            return 'Sell', 'RSI is above 70'
        return 'Hold', 'RSI is between 30 and 70'

    def analyze_macd(self):
        macd_above_signal = self.data['MACD'].iloc[-1] > self.data['Signal Line'].iloc[-1]
        macd_crossed_above = self.data['MACD'].iloc[-2] <= self.data['Signal Line'].iloc[-2]
        if macd_above_signal and macd_crossed_above:
            return 'Buy', 'MACD crossed above Signal Line'
        elif not macd_above_signal and not macd_crossed_above:
            return 'Sell', 'MACD crossed below Signal Line'
        return 'Hold', 'No significant crossover'

    def analyze_bollinger_bands(self):
        if self.data['Close'].iloc[-1] > self.data['Upper Band'].iloc[-1]:
            return 'Sell', 'Price is above the Upper Bollinger Band'
        elif self.data['Close'].iloc[-1] < self.data['Lower Band'].iloc[-1]:
            return 'Buy', 'Price is below the Lower Bollinger Band'
        return 'Hold', 'Price is between the Bollinger Bands'

    def analyze_stochastic_oscillator(self):
        if self.data['%K'].iloc[-1] < 20:
            return 'Buy', '%K is below 20'
        elif self.data['%K'].iloc[-1] > 80:
            return 'Sell', '%K is above 80'
        return 'Hold', '%K is between 20 and 80'

    def aggregate_advice(self, *advices):
        advice_map = {'Strong Buy': 2, 'Buy': 1, 'Hold': 0, 'Sell': -1, 'Strong Sell': -2}
        advice_scores = [advice_map.get(advice, 0) for advice, reason in advices]
        total_score = sum(advice_scores)
        confidence = abs(total_score) / (2 * len(advices))  # Normalize confidence to [0, 1]

        if total_score >= 4:
            return 'Strong Buy', confidence
        elif total_score >= 1:
            return 'Buy', confidence
        elif total_score <= -4:
            return 'Strong Sell', confidence
        elif total_score <= -1:
            return 'Sell', confidence
        return 'Hold', confidence

    def generate_pdf_report(self, general_advice):
        os.makedirs(self.ticker, exist_ok=True)
        pdf_path = f'{self.ticker}/{self.ticker}_strategy_report_{self.term}.pdf'
        recommendations = []
        current_price = self.data['Close'].iloc[-1]
        with PdfPages(pdf_path) as pdf:
            # Plot current price prominently
            fig, ax = plt.subplots(figsize=(10, 2))
            ax.text(0.5, 0.7, f'Current Price: ${current_price:.2f}', fontsize=24, ha='center', va='center', fontweight='bold')
            ax.text(0.5, 0.3, f'General Advice: {general_advice}', fontsize=24, ha='center', va='center', fontweight='bold', color='blue')
            ax.axis('off')
            pdf.savefig(fig)
            plt.close(fig)
            
            for strategy_method in [self.calculate_rsi, self.calculate_bollinger_bands, self.calculate_pivot_points]:
                plt.figure(figsize=(10, 5))
                strategy_method()
                advice, reason = self.advice_for_method(strategy_method.__name__)
                recommendations.append((strategy_method.__name__.replace('calculate_', '').replace('_', ' ').title(), advice, reason, current_price))
                self.plot(strategy_method.__name__)
                pdf.savefig()
                plt.close()
            # no plot only recommandations
            for strategy_method in [self.calculate_macd, self.calculate_moving_averages, self.calculate_stochastic_oscillator]:
                advice, reason = self.advice_for_method(strategy_method.__name__)
                recommendations.append((strategy_method.__name__.replace('calculate_', '').replace('_', ' ').title(), advice, reason, current_price))
                
            self.add_recommendations_table(pdf, recommendations)
            self.add_pivot_points_table(pdf)  # Add pivot points after recommendations table

    def advice_for_method(self, method_name):
        if method_name == 'calculate_moving_averages':
            return self.analyze_moving_averages()
        elif method_name == 'calculate_rsi':
            return self.analyze_rsi()
        elif method_name == 'calculate_macd':
            return self.analyze_macd()
        elif method_name == 'calculate_bollinger_bands':
            return self.analyze_bollinger_bands()
        elif method_name == 'calculate_stochastic_oscillator':
            return self.analyze_stochastic_oscillator()
        return 'Hold', 'No advice available'

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
        elif strategy_name == 'calculate_bollinger_bands':
            plt.plot(self.data['Close'], label='Close Price')
            plt.plot(self.data['Upper Band'], label='Upper Band', color='red')
            plt.plot(self.data['Lower Band'], label='Lower Band', color='green')
            plt.legend()
        elif strategy_name == 'calculate_stochastic_oscillator':
            plt.plot(self.data['%K'], label='%K', color='blue')
            plt.plot(self.data['%D'], label='%D', color='red')
            plt.legend()
        elif strategy_name == 'calculate_pivot_points':
            plt.plot(self.data['Close'], label='Close Price')
            self.plot_pivot_points()
        plt.tight_layout()

    def plot_signals(self):
        buy_signals = self.data[self.data['positions'] == 1]
        sell_signals = self.data[self.data['positions'] == -1]
        plt.plot(buy_signals.index, self.data['Close'][buy_signals.index], '^', markersize=10, color='g', label='Buy Signal')
        plt.plot(sell_signals.index, self.data['Close'][sell_signals.index], 'v', markersize=10, color='r', label='Sell Signal')
        plt.legend()

    def plot_pivot_points(self):
        plt.axhline(y=self.pivot_data['Pivot'].iloc[-1], color='black', linestyle='--', label='Pivot')
        plt.axhline(y=self.pivot_data['R1'].iloc[-1], color='red', linestyle='--', label='R1')
        plt.axhline(y=self.pivot_data['S1'].iloc[-1], color='green', linestyle='--', label='S1')
        plt.axhline(y=self.pivot_data['R2'].iloc[-1], color='red', linestyle='--', label='R2')
        plt.axhline(y=self.pivot_data['S2'].iloc[-1], color='green', linestyle='--', label='S2')
        plt.axhline(y=self.pivot_data['R3'].iloc[-1], color='red', linestyle='--', label='R3')
        plt.axhline(y=self.pivot_data['S3'].iloc[-1], color='green', linestyle='--', label='S3')
        plt.legend()

    def add_recommendations_table(self, pdf, recommendations):
        fig, ax = plt.subplots(figsize=(10, 2))
        ax.axis('tight')
        ax.axis('off')
        table = ax.table(cellText=recommendations, colLabels=['Strategy', 'Advice', 'Reason', 'Current Value'], cellLoc='center', loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.auto_set_column_width(col=list(range(len(recommendations[0]))))
        pdf.savefig()
        plt.close()

    def add_pivot_points_table(self, pdf):
        pivot_points = self.pivot_data[['Pivot', 'R1', 'R2', 'R3', 'S1', 'S2', 'S3']].iloc[-1]
        fig, ax = plt.subplots(figsize=(10, 2))
        ax.axis('tight')
        ax.axis('off')
        table = ax.table(cellText=[pivot_points.values], colLabels=pivot_points.index, cellLoc='center', loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.auto_set_column_width(col=list(range(len(pivot_points))))
        pdf.savefig()
        plt.close()