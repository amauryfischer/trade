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
    def __init__(self, ticker, term='short', pivot_type='Traditional'):
        self.ticker = ticker
        self.term = term
        self.pivot_type = pivot_type
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
        
        pp = PivotPoints(self.yesterday_data)
        self.pivot_data = pp.calculate()

    def advice(self):
        self.calculate_indicators()
        
        ma_score = MovingAverage(self.data, self.short_window, self.long_window).analyze()
        rsi_score = RSI(self.data, self.rsi_window).analyze()
        macd_score = MACD(self.data, self.macd_short, self.macd_long, self.macd_signal).analyze()
        bb_score = BollingerBands(self.data, 20).analyze()
        so_score = StochasticOscillator(self.data, 14).analyze()
        pivot_score = PivotPoints(self.pivot_data).analyze()
        
        final_score = self.aggregate_scores(ma_score, rsi_score, macd_score, bb_score, so_score, pivot_score)
        return final_score

    def aggregate_scores(self, *scores):
        average_score = sum(scores) / len(scores)
        return average_score

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
                score = indicator.analyze()
                current_value = self.get_current_indicator_value(indicator)
                recommendations.append((indicator.__class__.__name__, score, current_value))
            
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
        table = ax.table(cellText=recommendations, colLabels=['Strategy', 'Score', 'Current Value'], cellLoc='center', loc='center')
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
