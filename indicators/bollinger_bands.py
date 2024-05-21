import matplotlib.pyplot as plt

class BollingerBands:
    def __init__(self, data, window):
        self.data = data
        self.window = window

    def calculate(self):
        self.data['20_MA'] = self.data['Close'].rolling(window=self.window).mean()
        self.data['20_STD'] = self.data['Close'].rolling(window=self.window).std()
        self.data['Upper Band'] = self.data['20_MA'] + (self.data['20_STD'] * 2)
        self.data['Lower Band'] = self.data['20_MA'] - (self.data['20_STD'] * 2)
        return self.data

    def analyze(self):
        if self.data['Close'].iloc[-1] > self.data['Upper Band'].iloc[-1]:
            return 'Sell', 'Price is above the Upper Bollinger Band'
        elif self.data['Close'].iloc[-1] < self.data['Lower Band'].iloc[-1]:
            return 'Buy', 'Price is below the Lower Bollinger Band'
        return 'Hold', 'Price is between the Bollinger Bands'

    def plot(self):
        plt.plot(self.data['Close'], label='Close Price')
        plt.plot(self.data['Upper Band'], label='Upper Band', color='red')
        plt.plot(self.data['Lower Band'], label='Lower Band', color='green')
        plt.legend()
        plt.title('Bollinger Bands')
        plt.tight_layout()
