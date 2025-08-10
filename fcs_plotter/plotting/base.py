from abc import ABC, abstractmethod
from PyQt6.QtWidgets import QWidget
import pandas as pd


class BasePlotter(ABC):
    """Abstract base class for plotters."""

    @abstractmethod
    def get_widget(self) -> QWidget:
        """Return the plot widget."""
        pass

    @abstractmethod
    def plot_data(
        self,
        df: pd.DataFrame,
        x_channel: str,
        y_channel: str,
        spot_size: int,  # Size of the spots in pixels
        spot_alpha: float,  # 0 to 1, where 0 is fully transparent and 1 is fully opaque
        quantile: float,  # 0 to 1, ratio of data to include in the quantile plot range, larger values include more data
        range_margin: float,  # 0 to 1, increases plot around the quantile range by this factor (e.g. 0.1 means 10% of the range on each side is added to the plot limits)
        ratio: float,  # 0 to 1, ratio of points to plot
    ):
        """Plot the data from the dataframe."""
        pass

    @abstractmethod
    def clear(self):
        """Clear the plot."""
        pass
