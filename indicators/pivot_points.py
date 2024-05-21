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
        s3 = self.data['S3'].iloc[-1]
        s2 = self.data['S2'].iloc[-1]
        s1 = self.data['S1'].iloc[-1]
        r1 = self.data['R1'].iloc[-1]
        r2 = self.data['R2'].iloc[-1]
        r3 = self.data['R3'].iloc[-1]

        if close < s3:
            score = 0  # Very strong sell
        elif close > r3:
            score = 100  # Very strong buy
        elif close < s2:
            score = 30 * (close - s3) / (s2 - s3)  # Map S3-S2 to 0-30
        elif close < s1:
            score = 30 + 20 * (close - s2) / (s1 - s2)  # Map S2-S1 to 30-50
        elif close < pivot:
            score = 50 + 20 * (close - s1) / (pivot - s1)  # Map S1-Pivot to 50-70
        elif close < r1:
            score = 70 + 20 * (close - pivot) / (r1 - pivot)  # Map Pivot-R1 to 70-90
        elif close < r2:
            score = 90 + 10 * (close - r1) / (r2 - r1)  # Map R1-R2 to 90-100
        else:
            score = 100  # Very strong buy

        return score

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
