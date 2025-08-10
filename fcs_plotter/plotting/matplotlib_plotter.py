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
        quantile: float,
        range_margin: float,
    ):
        self.clear()
        # Use a copy to avoid SettingWithCopyWarning
        df_plot = df.copy()
        df_plot["filename"] = df_plot["file_path"].apply(lambda x: x.split("/")[-1])
        sns.scatterplot(
            data=df_plot,
            x=x_channel,
            y=y_channel,
            hue="filename",
            s=spot_size,
            alpha=spot_alpha,
            ax=self.ax,
            linewidth=0,
        )

        # Calculate and set plot ranges
        if not df_plot.empty:
            lower_q = (1 - quantile) / 2
            upper_q = 1 - lower_q

            x_min = df_plot[x_channel].quantile(lower_q)
            x_max = df_plot[x_channel].quantile(upper_q)
            x_range = x_max - x_min
            self.ax.set_xlim(x_min - x_range * range_margin, x_max + x_range * range_margin)

            y_min = df_plot[y_channel].quantile(lower_q)
            y_max = df_plot[y_channel].quantile(upper_q)
            y_range = y_max - y_min
            self.ax.set_ylim(y_min - y_range * range_margin, y_max + y_range * range_margin)

        self.ax.set_xscale("log")
        self.ax.set_yscale("log")
        self.ax.set_xlabel(x_channel)
        self.ax.set_ylabel(y_channel)
        self.ax.set_title(f"{y_channel} vs {x_channel}")
        self.ax.grid(True)
        self.canvas.draw()

    def clear(self):
        self.ax.clear()
        self.canvas.draw()
