# start of ./plotting/fastplotlib_plotter.py
import fastplotlib as fpl
import numpy as np
import pandas as pd
from PyQt6.QtWidgets import QWidget
from pandas.plotting import autocorrelation_plot

from .base import BasePlotter


class FastplotlibPlotter(BasePlotter):
    """
    A minimal, high-performance plotter using fastplotlib.
    This version plots all points as a single scatter graphic with a default color.
    """

    def __init__(self):
        # Create a fastplotlib Figure. This is the main plotting object.
        self.figure = fpl.Figure()

        # The .show() method returns the Qt widget that can be embedded in an application.
        self._widget = self.figure.show()

        # Get the first subplot to add graphics to.
        self.subplot = self.figure[0, 0]
        self.scatter_graphic = None

        # Set log scale for axes, which is common for FCS data.
        self.subplot.axes.x.scale = "log"
        self.subplot.axes.y.scale = "log"

    def get_widget(self) -> QWidget:
        """Return the underlying PyQt widget for the plot."""
        return self._widget

    def plot_data(
            self,
            df: pd.DataFrame,
            x_channel: str,
            y_channel: str,
            spot_size: int,
            spot_alpha: float,  # Note: spot_alpha is ignored in this minimal version
            quantile: float,
            range_margin: float,
            ratio: float,
    ):
        """Plots scatter data using a single, simple fastplotlib scatter graphic."""
        self.clear()

        if df is None or df.empty:
            return

        df_plot = df.copy()

        # Downsample data if ratio is less than 1.0
        if ratio < 1.0:
            df_plot = df_plot.sample(frac=ratio, random_state=1)

        # Filter out non-positive values which cannot be displayed on a log scale
        df_plot = df_plot[(df_plot[x_channel] > 0) & (df_plot[y_channel] > 0)]
        if df_plot.empty:
            return  # No valid data to plot

        # Prepare data for a single scatter plot. No grouping, no custom colors.
        data = df_plot[[x_channel, y_channel]].values.astype(np.float32)

        # Add the single scatter graphic. fastplotlib will use a default color.
        self.scatter_graphic = self.subplot.add_scatter(data=data, sizes=spot_size, alpha=spot_alpha)
        print(self.scatter_graphic.axes)


        # Calculate and set plot ranges based on quantiles
        lower_q = (1 - quantile) / 2
        upper_q = 1 - lower_q

        x_min_q = df_plot[x_channel].quantile(lower_q)
        x_max_q = df_plot[x_channel].quantile(upper_q)
        x_range = x_max_q - x_min_q
        if x_range <= 0:
            x_range = x_max_q * 0.1 if x_max_q > 0 else 1.0
        x_min = x_min_q - x_range * range_margin
        x_max = x_max_q + x_range * range_margin

        y_min_q = df_plot[y_channel].quantile(lower_q)
        y_max_q = df_plot[y_channel].quantile(upper_q)
        y_range = y_max_q - y_min_q
        if y_range <= 0:
            y_range = y_max_q * 0.1 if y_max_q > 0 else 1.0
        y_min = y_min_q - y_range * range_margin
        y_max = y_max_q + y_range * range_margin

        # Set camera to frame the desired data range
        self.subplot.camera.width = x_max - x_min
        self.subplot.camera.local.x = (x_min + x_max) / 2
        self.subplot.camera.height = y_max - y_min
        self.subplot.camera.local.y = (y_min + y_max) / 2

        # Set labels, title, and grid
        # self.subplot.axes.x.set_label(x_channel)
        # self.subplot.axes.y.set_label(y_channel)
        # self.subplot.set_title(f"{y_channel} vs {x_channel}")
        # self.subplot.axes.x.set_grid(True)
        # self.subplot.axes.y.set_grid(True)

    def clear(self):
        """Removes all graphics from the plot."""
        if self.scatter_graphic is not None:
            self.subplot.remove_graphic(self.scatter_graphic)
            self.scatter_graphic = None
        # Reset the view after clearing the plot.
        self.subplot.auto_scale(maintain_aspect=False)