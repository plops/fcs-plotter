from .matplotlib_plotter import MatplotlibPlotter
from .pyqtgraph_plotter import PyQtGraphPlotter
from .fastplotlib_plotter import FastplotlibPlotter

PLOTTERS = {
    "pyqtgraph": PyQtGraphPlotter,
    "matplotlib": MatplotlibPlotter,
    "fastplotlib": FastplotlibPlotter,
}

PLOTTER_NAMES = list(PLOTTERS.keys())


def get_plotter(name: str = "pyqtgraph"):
    """
    Factory function to get a plotter instance.
    """
    plotter_class = PLOTTERS.get(name)
    if plotter_class:
        return plotter_class()
    raise ValueError(f"Unknown plotter: {name}")
