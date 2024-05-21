import matplotlib.pyplot as plt

class MACD:
    def __init__(self, data, short_span, long_span, signal_span):
        self.data = data
        self.short_span = short_span
        self.long_span = long_span
        self.signal_span = signal_span

    def calculate(self):
        exp1 = self.data['Close'].ewm(span=self.short_span, adjust=False).mean()
        exp2 = self.data['Close'].ewm(span=self.long_span, adjust=False).mean()
        self.data['MACD'] = exp1 - exp2
        self.data['Signal Line'] = self.data['MACD'].ewm(span=self.signal_span, adjust=False).mean()
        return self.data

    def analyze(self):
        macd_above_signal = self.data['MACD'].iloc[-1] > self.data['Signal Line'].iloc[-1]
        macd_crossed_above = self.data['MACD'].iloc[-2] <= self.data['Signal Line'].iloc[-2]
        if macd_above_signal and macd_crossed_above:
            return 'Buy', 'MACD crossed above Signal Line'
        elif not macd_above_signal and not macd_crossed_above:
            return 'Sell', 'MACD crossed below Signal Line'
        return 'Hold', 'No significant crossover'

    def plot(self):
        plt.plot(self.data['MACD'], label='MACD', color='blue')
        plt.plot(self.data['Signal Line'], label='Signal Line', color='red')
        plt.legend()
        plt.title('MACD')
        plt.tight_layout()
