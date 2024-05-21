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
        macd = self.data['MACD'].iloc[-1]
        signal = self.data['Signal Line'].iloc[-1]
        difference = macd - signal
        
        # Determine the score based on the difference
        if difference > 0:
            score = min(100, 50 + (difference / signal) * 50)  # Cap the score at 100
        else:
            score = max(0, 50 + (difference / signal) * 50)  # Cap the score at 0

        return score

    def plot(self):
        plt.plot(self.data['MACD'], label='MACD', color='blue')
        plt.plot(self.data['Signal Line'], label='Signal Line', color='red')
        plt.legend()
        plt.title('MACD')
        plt.tight_layout()
