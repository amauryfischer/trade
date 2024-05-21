import matplotlib.pyplot as plt

class PivotPoints:
    def __init__(self, data):
        self.data = data

    def calculate(self):
        max_value = self.data['High'].max()
        min_value = self.data['Low'].min()
        close = self.data['Close'].iloc[-1]
        self.data['Pivot'] = (max_value + min_value + close) / 3
        self.data['R1'] = 2 * self.data['Pivot'] - min_value
        self.data['S1'] = 2 * self.data['Pivot'] - max_value
        self.data['R2'] = self.data['Pivot'] + (max_value - min_value)
        self.data['S2'] = self.data['Pivot'] - (max_value - min_value)
        self.data['R3'] = max_value + 2 * (self.data['Pivot'] - min_value)
        self.data['S3'] = min_value - 2 * (max_value - self.data['Pivot'])
        return self.data

    def analyze(self):
        close = self.data['Close'].iloc[-1]
        pivot = self.data['Pivot'].iloc[-1]
        if close > pivot:
            return 'Buy', 'Price is above the Pivot Point'
        elif close < pivot:
            return 'Sell', 'Price is below the Pivot Point'
        return 'Hold', 'Price is around the Pivot Point'

    def plot(self):
        plt.plot(self.data['Close'], label='Close Price')
        plt.axhline(y=self.data['Pivot'].iloc[-1], color='black', linestyle='--', label='Pivot')
        plt.axhline(y=self.data['R1'].iloc[-1], color='red', linestyle='--', label='R1')
        plt.axhline(y=self.data['S1'].iloc[-1], color='green', linestyle='--', label='S1')
        plt.axhline(y=self.data['R2'].iloc[-1], color='red', linestyle='--', label='R2')
        plt.axhline(y=self.data['S2'].iloc[-1], color='green', linestyle='--', label='S2')
        plt.axhline(y=self.data['R3'].iloc[-1], color='red', linestyle='--', label='R3')
        plt.axhline(y=self.data['S3'].iloc[-1], color='green', linestyle='--', label='S3')
        plt.legend()
        plt.title('Pivot Points')
        plt.tight_layout()
