import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class MovingAverage:
    def __init__(self, data, short_window, long_window):
        self.data = data
        self.short_window = short_window
        self.long_window = long_window

    def calculate(self):
        self.data['short_mavg'] = self.data['Close'].rolling(window=self.short_window).mean()
        self.data['long_mavg'] = self.data['Close'].rolling(window=self.long_window).mean()
        self.data['positions'] = pd.Series(np.where(self.data['short_mavg'] > self.data['long_mavg'], 1, 0), index=self.data.index).diff().fillna(0)
        return self.data

    def analyze(self):
        latest_position = self.data['positions'].iloc[-1]
        if latest_position == 1:
            return 'Buy', 'Short MA crossed above Long MA'
        elif latest_position == -1:
            return 'Sell', 'Short MA crossed below Long MA'
        return 'Hold', 'No significant crossover'

    def plot(self):
        plt.plot(self.data['Close'], label='Close Price')
        plt.plot(self.data['short_mavg'], label=f'{self.short_window}-Day MA')
        plt.plot(self.data['long_mavg'], label=f'{self.long_window}-Day MA')
        self.plot_signals()
        plt.legend()
        plt.title('Moving Averages')
        plt.tight_layout()

    def plot_signals(self):
        buy_signals = self.data[self.data['positions'] == 1]
        sell_signals = self.data[self.data['positions'] == -1]
        plt.plot(buy_signals.index, self.data['Close'][buy_signals.index], '^', markersize=10, color='g', label='Buy Signal')
        plt.plot(sell_signals.index, self.data['Close'][sell_signals.index], 'v', markersize=10, color='r', label='Sell Signal')
