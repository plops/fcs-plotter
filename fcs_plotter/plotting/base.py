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
        spot_size: int,
        spot_alpha: float,
    ):
        """Plot the data from the dataframe."""
        pass

    @abstractmethod
    def clear(self):
        """Clear the plot."""
        pass


