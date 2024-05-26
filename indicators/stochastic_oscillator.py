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
            # Linear interpolation from 0 to 20 %K to 70 to 100 score
            score = 70 + (current_k / 20) * 30
        elif current_k > 80:
            # Linear interpolation from 80 to 100 %K to 30 to 0 score
            score = 30 * (100 - current_k) / 20
        else:
            # Linear interpolation from 20 to 80 %K to 30 to 70 score
            score = 30 + (current_k - 20) * 40 / 60
        
        # Ensure score is within 0-100
        score = max(0, min(100, score))
        
        return score


    def plot(self):
        plt.plot(self.data['%K'], label='%K', color='blue')
        plt.plot(self.data['%D'], label='%D', color='red')
        plt.axhline(80, linestyle='--', color='red')
        plt.axhline(20, linestyle='--', color='green')
        plt.legend()
        plt.title('Stochastic Oscillator')
        plt.tight_layout()
