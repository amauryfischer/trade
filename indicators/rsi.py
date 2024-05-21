import matplotlib.pyplot as plt

class RSI:
    def __init__(self, data, window):
        self.data = data
        self.window = window

    def calculate(self):
        delta = self.data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(self.window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(self.window).mean()
        rs = gain / loss
        self.data['RSI'] = 100 - (100 / (1 + rs))
        return self.data

    def analyze(self):
        current_rsi = self.data['RSI'].iloc[-1]
        if current_rsi < 30:
            return 'Buy', 'RSI is below 30'
        elif current_rsi > 70:
            return 'Sell', 'RSI is above 70'
        return 'Hold', 'RSI is between 30 and 70'

    def plot(self):
        plt.subplot(2, 1, 1)
        plt.plot(self.data['Close'], label='Close Price')
        plt.legend()
        plt.title('Close Price')
        plt.subplot(2, 1, 2)
        plt.plot(self.data['RSI'], label='RSI', color='purple')
        plt.axhline(70, linestyle='--', color='red')
        plt.axhline(30, linestyle='--', color='green')
        plt.legend()
        plt.title('RSI')
        plt.tight_layout()
