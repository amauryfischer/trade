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

        def linear_interpolate(x, x0, x1, y0, y1):
            return y0 + (x - x0) * (y1 - y0) / (x1 - x0)

        if close <= s3:
            score = linear_interpolate(close, s3, s3, 30, 30)  # Close at or below S3, score is 30
        elif s3 < close <= s2:
            score = linear_interpolate(close, s3, s2, 30, 50)  # Interpolate between S3 (30) and S2 (50)
        elif s2 < close <= s1:
            score = linear_interpolate(close, s2, s1, 50, 70)  # Interpolate between S2 (50) and S1 (70)
        elif s1 < close <= pivot:
            score = linear_interpolate(close, s1, pivot, 70, 50)  # Interpolate between S1 (70) and pivot (50)
        elif pivot < close <= r1:
            score = linear_interpolate(close, pivot, r1, 50, 70)  # Interpolate between pivot (50) and R1 (70)
        elif r1 < close <= r2:
            score = linear_interpolate(close, r1, r2, 70, 90)  # Interpolate between R1 (70) and R2 (90)
        elif r2 < close <= r3:
            score = linear_interpolate(close, r2, r3, 90, 100)  # Interpolate between R2 (90) and R3 (100)
        else:
            score = linear_interpolate(close, r3, r3, 100, 100)  # Close at or above R3, score is 100

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
