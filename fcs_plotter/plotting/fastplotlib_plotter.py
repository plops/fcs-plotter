# start of ./plotting/fastplotlib_plotter.py
import fastplotlib as fpl
import numpy as np
import pandas as pd
from PyQt6.QtWidgets import QWidget
import pyqtgraph as pg

from .base import BasePlotter


class FastplotlibPlotter(BasePlotter):
    """A plotter using the high-performance fastplotlib library."""

    def __init__(self):
        # Create a fastplotlib Figure. This is the main plotting object.
        self.figure = fpl.Figure()

        # The .show() method returns the Qt widget that can be embedded in an application.
        # This is the correct and robust way to integrate fastplotlib into a PyQt app.
        self._widget = self.figure.show()

        # Get the first subplot to add graphics to.
        self.subplot = self.figure[0, 0]
        self.scatter_graphics = []

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
            spot_alpha: float,
            quantile: float,
            range_margin: float,
            ratio: float,
    ):
        """Plots scatter data using fastplotlib."""
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

        # Generate a color palette for the unique files
        unique_files = df_plot["file_path"].unique()
        palette = pg.colormap.get("viridis", "matplotlib").getColors(
            mode="float", count=len(unique_files)
        )
        color_map = {file: color for file, color in zip(unique_files, palette)}

        # Plot each file's data as a separate scatter graphic
        for file_path, group in df_plot.groupby("file_path"):
            data = group[[x_channel, y_channel]].values.astype(np.float32)
            if data.shape[0] == 0:
                continue

            color = color_map[file_path]
            # Set the alpha value from the UI control
            final_color = (color[0], color[1], color[2], spot_alpha)

            scatter = self.subplot.add_scatter(
                data=data,
                sizes=spot_size,
                colors=final_color,  # Use a single color tuple for efficiency
                name=file_path.split("/")[-1],
            )
            self.scatter_graphics.append(scatter)

        # Calculate and set plot ranges based on quantiles
        if not df_plot.empty:
            lower_q = (1 - quantile) / 2
            upper_q = 1 - lower_q

            x_min = df_plot[x_channel].quantile(lower_q)
            x_max = df_plot[x_channel].quantile(upper_q)
            x_range = x_max - x_min
            if x_range <= 0:
                x_range = x_max * 0.1 if x_max > 0 else 1.0  # Handle zero-range data
            self.subplot.axes.x.lim = (
                x_min - x_range * range_margin,
                x_max + x_range * range_margin,
            )

            y_min = df_plot[y_channel].quantile(lower_q)
            y_max = df_plot[y_channel].quantile(upper_q)
            y_range = y_max - y_min
            if y_range <= 0:
                y_range = y_max * 0.1 if y_max > 0 else 1.0  # Handle zero-range data
            self.subplot.axes.y.lim = (
                y_min - y_range * range_margin,
                y_max + y_range * range_margin,
            )

        # Set labels, title, and grid
        self.subplot.axes.x.set_label(x_channel)
        self.subplot.axes.y.set_label(y_channel)
        self.subplot.set_title(f"{y_channel} vs {x_channel}")
        self.subplot.axes.x.set_grid(True)
        self.subplot.axes.y.set_grid(True)

    def clear(self):
        """Removes all graphics from the plot."""
        if hasattr(self, "subplot"):
            for scatter in self.scatter_graphics:
                self.subplot.remove_graphic(scatter)
            self.scatter_graphics.clear()
            # Reset the view after clearing the plot
            self.subplot.auto_scale(maintain_aspect=False, pad=0.05)