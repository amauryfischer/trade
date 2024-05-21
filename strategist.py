import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from indicators.moving_average import MovingAverage
from indicators.rsi import RSI
from indicators.macd import MACD
from indicators.bollinger_bands import BollingerBands
from indicators.stochastic_oscillator import StochasticOscillator
from indicators.pivot_points import PivotPoints


class Strategist:
    def __init__(self, ticker, term='short', pivot_type='Traditional', pivot_timeframe='daily'):
        self.ticker = ticker
        self.term = term
        self.pivot_type = pivot_type
        self.pivot_timeframe = pivot_timeframe
        self.setup_term_parameters(term)
        self.data = yf.Ticker(ticker).history(period=self.period, interval=self.interval)
        self.daily_data = yf.Ticker(ticker).history(period='1d', interval='1m')  # Fetch daily data for pivot points
        last_5_days = yf.Ticker(ticker).history(period='5d', interval='1m')
        last_5_days.sort_index(inplace=True)

        # Calculate yesterday's date
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)

        # Filter out the data for yesterday
        self.yesterday_data = last_5_days[(last_5_days.index.date == yesterday)]

        self.set_pivot_timeframe_data()

    def setup_term_parameters(self, term):
        terms = {
            'very_short': ('1d', '1m', 3, 10, 9, 3, 10, 5),
            'short': ('1d', '1m', 5, 20, 14, 12, 26, 9),
            'medium': ('1mo', '1h', 12, 26, 14, 12, 26, 9),
            'long': ('1y', '1d', 50, 200, 14, 12, 26, 9),
        }
        if term in terms:
            self.period, self.interval, self.short_window, self.long_window, self.rsi_window, self.macd_short, self.macd_long, self.macd_signal = terms[term]
        else:
            raise ValueError("Term must be 'very_short', 'short', 'medium', or 'long'")

    def set_pivot_timeframe_data(self):
        if self.pivot_timeframe == 'daily':
            self.pivot_data = self.yesterday_data
        elif self.pivot_timeframe == 'weekly':
            self.pivot_data = self.daily_data.resample('W').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'})
        elif self.pivot_timeframe == 'monthly':
            self.pivot_data = self.daily_data.resample('M').agg({'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last'})
        else:
            raise ValueError("Pivot timeframe must be 'daily', 'weekly', or 'monthly'")

    def calculate_indicators(self):
        ma = MovingAverage(self.data, self.short_window, self.long_window)
        self.data = ma.calculate()
        
        rsi = RSI(self.data, self.rsi_window)
        self.data = rsi.calculate()
        
        macd = MACD(self.data, self.macd_short, self.macd_long, self.macd_signal)
        self.data = macd.calculate()
        
        bb = BollingerBands(self.data, 20)
        self.data = bb.calculate()
        
        so = StochasticOscillator(self.data, 14)
        self.data = so.calculate()
        
        pp = PivotPoints(self.pivot_data)
        self.pivot_data = pp.calculate()

    def advice(self):
        self.calculate_indicators()
        
        mac_advice, mac_reason = MovingAverage(self.data, self.short_window, self.long_window).analyze()
        rsi_advice, rsi_reason = RSI(self.data, self.rsi_window).analyze()
        macd_advice, macd_reason = MACD(self.data, self.macd_short, self.macd_long, self.macd_signal).analyze()
        bb_advice, bb_reason = BollingerBands(self.data, 20).analyze()
        so_advice, so_reason = StochasticOscillator(self.data, 14).analyze()
        pivot_advice, pivot_reason = PivotPoints(self.pivot_data).analyze()
        
        final_advice, confidence = self.aggregate_advice(
            (mac_advice, mac_reason), 
            (rsi_advice, rsi_reason), 
            (macd_advice, macd_reason), 
            (bb_advice, bb_reason), 
            (so_advice, so_reason), 
            (pivot_advice, pivot_reason)
        )
        return final_advice, confidence

    def aggregate_advice(self, *advices):
        advice_map = {'Strong Buy': 2, 'Buy': 1, 'Hold': 0, 'Sell': -1, 'Strong Sell': -2}
        advice_scores = [advice_map.get(advice, 0) for advice, reason in advices]
        total_score = sum(advice_scores)
        confidence = abs(total_score) / (2 * len(advices))  # Normalize confidence to [0, 1]

        if total_score >= 4:
            return 'Strong Buy', confidence
        elif total_score >= 1:
            return 'Buy', confidence
        elif total_score <= -4:
            return 'Strong Sell', confidence
        elif total_score <= -1:
            return 'Sell', confidence
        return 'Hold', confidence

    def generate_pdf_report(self, general_advice):
        report_dir = os.path.join('reports', self.ticker)
        os.makedirs(report_dir, exist_ok=True)
        pdf_path = os.path.join(report_dir, f'{self.ticker}_strategy_report_{self.term}.pdf')
        recommendations = []
        
        with PdfPages(pdf_path) as pdf:
            # Create recommendations table first
            for IndicatorClass, params in [
                (RSI, {'window': self.rsi_window}),
                (BollingerBands, {'window': 20}),
                (PivotPoints, {}),
                (MACD, {'short_span': self.macd_short, 'long_span': self.macd_long, 'signal_span': self.macd_signal}),
                (MovingAverage, {'short_window': self.short_window, 'long_window': self.long_window}),
                (StochasticOscillator, {'window': 14})
            ]:
                indicator = IndicatorClass(self.data, **params)
                indicator.calculate()
                advice, reason = indicator.analyze()
                current_value = self.get_current_indicator_value(indicator)
                recommendations.append((indicator.__class__.__name__, advice, reason, current_value))
            
            self.add_recommendations_table(pdf, recommendations)
            
            # Plot general advice prominently
            fig, ax = plt.subplots(figsize=(10, 2))
            ax.text(0.5, 0.5, f'General Advice: {general_advice}', fontsize=24, ha='center', va='center', fontweight='bold', color='blue')
            ax.axis('off')
            pdf.savefig(fig)
            plt.close(fig)
            
            # Plot strategies with charts
            for IndicatorClass, params in [
                (RSI, {'window': self.rsi_window}),
                (BollingerBands, {'window': 20}),
                (PivotPoints, {}),
            ]:
                indicator = IndicatorClass(self.data, **params)
                indicator.calculate()
                plt.figure(figsize=(10, 5))
                indicator.plot()
                pdf.savefig()
                plt.close()
                
            self.add_pivot_points_table(pdf)  # Add pivot points after strategy plots

    def get_current_indicator_value(self, indicator):
        if isinstance(indicator, RSI):
            return self.data['RSI'].iloc[-1]
        elif isinstance(indicator, BollingerBands):
            return self.data['Close'].iloc[-1]
        elif isinstance(indicator, PivotPoints):
            return self.pivot_data['Pivot'].iloc[-1]
        elif isinstance(indicator, MACD):
            return self.data['MACD'].iloc[-1]
        elif isinstance(indicator, MovingAverage):
            return self.data['Close'].iloc[-1]
        elif isinstance(indicator, StochasticOscillator):
            return self.data['%K'].iloc[-1]
        return 0.0

    def add_recommendations_table(self, pdf, recommendations):
        fig, ax = plt.subplots(figsize=(10, 2))
        ax.axis('tight')
        ax.axis('off')
        table = ax.table(cellText=recommendations, colLabels=['Strategy', 'Advice', 'Reason', 'Current Value'], cellLoc='center', loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.auto_set_column_width(col=list(range(len(recommendations[0]))))
        pdf.savefig()
        plt.close()

    def add_pivot_points_table(self, pdf):
        pivot_points = self.pivot_data[['Pivot', 'R1', 'R2', 'R3', 'S1', 'S2', 'S3']].iloc[-1]
        fig, ax = plt.subplots(figsize=(10, 2))
        ax.axis('tight')
        ax.axis('off')
        table = ax.table(cellText=[pivot_points.values], colLabels=pivot_points.index, cellLoc='center', loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.auto_set_column_width(col=list(range(len(pivot_points))))
        pdf.savefig()
        plt.close()

