import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget
import pandas as pd
import numpy as np
from .base import BasePlotter


class PyQtGraphPlotter(BasePlotter):
    """A plotter using pyqtgraph."""

    def __init__(self):
        pg.setConfigOption("imageAxisOrder", "row-major")
        pg.setConfigOption("background", "w")
        pg.setConfigOption("foreground", "k")
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.showGrid(x=True, y=True)
        self.legend = self.plot_widget.addLegend()
        self.scatter_items = []

    def get_widget(self) -> QWidget:
        return self.plot_widget

    def plot_data(
        self,
        df: pd.DataFrame,
        x_channel: str,
        y_channel: str,
        spot_size: int,
        spot_alpha: float,
        quantile: float,
        range_margin: float,
        ratio: float,
    ):
        self.clear()
        self.plot_widget.setLogMode(x=True, y=True)

        # pyqtgraph alpha is 0-255
        alpha = int(spot_alpha * 255)
        colors = self._get_colors(len(df["file_path"].unique()))

        df_to_plot = df
        if ratio < 1.0:
            df_to_plot = df.sample(frac=ratio)

        for i, (file_path, group) in enumerate(df_to_plot.groupby("file_path")):
            # Filter out non-positive values for log scale
            plot_group = group[(group[x_channel] > 0) & (group[y_channel] > 0)]
            if plot_group.empty:
                continue

            color = colors[i]
            brush = pg.mkBrush(color=color + (alpha,))
            # log how many points are being plotted
            print(f"Plotting {len(plot_group)} points for {file_path}")

            scatter = pg.ScatterPlotItem(
                x=plot_group[x_channel].values,
                y=plot_group[y_channel].values,
                size=spot_size,
                pxMode=True,  # Use pixel mode for size
                brush=brush,  # filling
                pen=None,  # no outline
                name=file_path.split("/")[-1],
                useCache=True,
            )
            self.plot_widget.addItem(scatter)
            self.scatter_items.append(scatter)

        # Calculate and set plot ranges
        if not df.empty:
            lower_q = (1 - quantile) / 2
            upper_q = 1 - lower_q

            x_min = df[x_channel].quantile(lower_q)
            x_max = df[x_channel].quantile(upper_q)
            x_range = x_max - x_min
            self.plot_widget.setXRange(
                np.log10(x_min - x_range * range_margin),
                np.log10(x_max + x_range * range_margin),
                padding=0,
            )

            y_min = df[y_channel].quantile(lower_q)
            y_max = df[y_channel].quantile(upper_q)
            y_range = y_max - y_min
            self.plot_widget.setYRange(
                np.log10(y_min - y_range * range_margin),
                np.log10(y_max + y_range * range_margin),
                padding=0,
            )

        self.plot_widget.setLabel("bottom", x_channel)
        self.plot_widget.setLabel("left", y_channel)
        self.plot_widget.setTitle(f"{y_channel} vs {x_channel}")

    def _get_colors(self, n):
        """Generate N distinct colors."""
        colors = []
        for i in range(n):
            hue = i / n
            color = pg.hsvColor(hue, sat=1.0, val=1.0, alpha=1.0).getRgb()[:3]
            colors.append(color)
        return colors

    def clear(self):
        for item in self.scatter_items:
            self.plot_widget.removeItem(item)
        self.scatter_items.clear()
        if self.legend:
            self.legend.clear()
