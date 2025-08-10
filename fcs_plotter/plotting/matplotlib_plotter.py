from PyQt6.QtWidgets import QWidget, QVBoxLayout
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from .base import BasePlotter


class MatplotlibPlotter(BasePlotter):
    """A plotter using Matplotlib and Seaborn."""

    def __init__(self):
        self.widget = QWidget()
        self.layout = QVBoxLayout(self.widget)
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)
        self.ax = self.figure.add_subplot(111)

    def get_widget(self) -> QWidget:
        return self.widget

    def plot_data(
        self,
        df: pd.DataFrame,
        x_channel: str,
        y_channel: str,
        spot_size: int,
        spot_alpha: float,
    ):
        self.clear()
        sns.scatterplot(
            data=df,
            x=x_channel,
            y=y_channel,
            s=spot_size,
            alpha=spot_alpha,
            ax=self.ax,
            legend=False,
            linewidth=0,
        )
        self.ax.set_xlabel(x_channel)
        self.ax.set_ylabel(y_channel)
        self.canvas.draw()

    def clear(self):
        self.ax.clear()
        self.canvas.draw()


