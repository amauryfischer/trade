import matplotlib.pyplot as plt

class StochasticOscillator:
    def __init__(self, data, window):
        self.data = data
        self.window = window

    def calculate(self):
        low_min = self.data['Low'].rolling(window=self.window).min()
        high_max = self.data['High'].rolling(window=self.window).max()
        self.data['%K'] = 100 * (self.data['Close'] - low_min) / (high_max - low_min)
        self.data['%D'] = self.data['%K'].rolling(window=3).mean()
        return self.data

    def analyze(self):
        if self.data['%K'].iloc[-1] < 20:
            return 'Buy', '%K is below 20'
        elif self.data['%K'].iloc[-1] > 80:
            return 'Sell', '%K is above 80'
        return 'Hold', '%K is between 20 and 80'

    def plot(self):
        plt.plot(self.data['%K'], label='%K', color='blue')
        plt.plot(self.data['%D'], label='%D', color='red')
        plt.legend()
        plt.title('Stochastic Oscillator')
        plt.tight_layout()
