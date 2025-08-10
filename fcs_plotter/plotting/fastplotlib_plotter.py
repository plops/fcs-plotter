import fastplotlib as fpl
import numpy as np
import pandas as pd
from PyQt6.QtWidgets import QWidget
import pyqtgraph as pg

from .base import BasePlotter


class FastplotlibPlotter(BasePlotter):
    """A plotter using fastplotlib."""

    def __init__(self):
        self.plot_widget = fpl.PlotWidget(make_pyqtgraph_widget=True)
        self.subplot = self.plot_widget[0, 0]
        self.scatter_graphics = []

    def get_widget(self) -> QWidget:
        return self.plot_widget.widget

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
        df_plot = df.copy()

        if ratio < 1.0:
            df_plot = df_plot.sample(frac=ratio, random_state=1)

        # Use seaborn to get a color palette
        unique_files = df_plot["file_path"].unique()
        palette = pg.colormap.get("viridis", "matplotlib").getColors(
            mode="float", count=len(unique_files)
        )
        color_map = {file: color for file, color in zip(unique_files, palette)}

        for file_path, group in df_plot.groupby("file_path"):
            data = group[[x_channel, y_channel]].values.astype(np.float32)
            color = np.array(color_map[file_path])
            color[3] = spot_alpha  # Set alpha
            colors = np.tile(color, (data.shape[0], 1))

            scatter = self.subplot.add_scatter(
                data=data, sizes=spot_size, colors=colors, name=file_path.split("/")[-1]
            )
            self.scatter_graphics.append(scatter)

        # Calculate and set plot ranges
        if not df_plot.empty:
            lower_q = (1 - quantile) / 2
            upper_q = 1 - lower_q

            x_min = df_plot[x_channel].quantile(lower_q)
            x_max = df_plot[x_channel].quantile(upper_q)
            x_range = x_max - x_min
            self.subplot.axes.x.lim = (
                x_min - x_range * range_margin,
                x_max + x_range * range_margin,
            )

            y_min = df_plot[y_channel].quantile(lower_q)
            y_max = df_plot[y_channel].quantile(upper_q)
            y_range = y_max - y_min
            self.subplot.axes.y.lim = (
                y_min - y_range * range_margin,
                y_max + y_range * range_margin,
            )

        self.subplot.axes.x.set_label(x_channel)
        self.subplot.axes.y.set_label(y_channel)
        self.subplot.set_title(f"{y_channel} vs {x_channel}")
        self.subplot.axes.x.set_grid(True)
        self.subplot.axes.y.set_grid(True)

    def clear(self):
        for scatter in self.scatter_graphics:
            self.subplot.remove_graphic(scatter)
        self.scatter_graphics.clear()
        self.subplot.auto_scale(maintain_aspect=False, pad=0.05)


