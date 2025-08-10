import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget
import pandas as pd
from .base import BasePlotter


class PyQtGraphPlotter(BasePlotter):
    """A plotter using pyqtgraph."""

    def __init__(self):
        pg.setConfigOption("imageAxisOrder", "row-major")
        self.plot_widget = pg.PlotWidget()
        self.scatter = pg.ScatterPlotItem()
        self.plot_widget.addItem(self.scatter)
        self.plot_widget.showGrid(x=True, y=True)

    def get_widget(self) -> QWidget:
        return self.plot_widget

    def plot_data(
        self,
        df: pd.DataFrame,
        x_channel: str,
        y_channel: str,
        spot_size: int,
        spot_alpha: float,
    ):
        self.clear()
        # pyqtgraph alpha is 0-255
        brush = pg.mkBrush(color=(0, 0, 255, int(spot_alpha * 255)))
        self.scatter.setData(
            x=df[x_channel].values,
            y=df[y_channel].values,
            size=spot_size,
            brush=brush,
            pen=None,
        )
        self.plot_widget.setLabel("bottom", x_channel)
        self.plot_widget.setLabel("left", y_channel)

    def clear(self):
        self.scatter.clear()


