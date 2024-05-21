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
        close = self.data['Close'].iloc[-1]
        upper_band = self.data['Upper Band'].iloc[-1]
        lower_band = self.data['Lower Band'].iloc[-1]
        middle_band = self.data['20_MA'].iloc[-1]

        if close > upper_band:
            score = max(0, 50 - (close - upper_band) / upper_band * 50)  # Cap the score at 0
        elif close < lower_band:
            score = min(100, 50 + (lower_band - close) / lower_band * 50)  # Cap the score at 100
        else:
            if close > middle_band:
                score = 50 + (close - middle_band) / (upper_band - middle_band) * 50  # Map Middle Band to Upper Band to 50-100
            else:
                score = 50 - (middle_band - close) / (middle_band - lower_band) * 50  # Map Lower Band to Middle Band to 0-50

        return score

    def plot(self):
        plt.plot(self.data['Close'], label='Close Price')
        plt.plot(self.data['Upper Band'], label='Upper Band', color='red')
        plt.plot(self.data['Lower Band'], label='Lower Band', color='green')
        plt.plot(self.data['20_MA'], label='20-Day MA', color='blue')
        plt.legend()
        plt.title('Bollinger Bands')
        plt.tight_layout()
