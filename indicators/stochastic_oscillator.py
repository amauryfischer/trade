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
        current_k = self.data['%K'].iloc[-1]
        
        if current_k < 20:
            score = 70 + ((20 - current_k) / 20) * 30  # Map 0-20 %K to 70-100 score
        elif current_k > 80:
            score = (100 - current_k) / 20 * 30  # Map 80-100 %K to 0-30 score
        else:
            score = 30 + ((current_k - 20) / 60) * 40  # Map 20-80 %K to 30-70 score
        
        return score

    def plot(self):
        plt.plot(self.data['%K'], label='%K', color='blue')
        plt.plot(self.data['%D'], label='%D', color='red')
        plt.axhline(80, linestyle='--', color='red')
        plt.axhline(20, linestyle='--', color='green')
        plt.legend()
        plt.title('Stochastic Oscillator')
        plt.tight_layout()
