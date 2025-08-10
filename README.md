# FCS Plotter

A PyQt6 application for reading and plotting FCS (Flow Cytometry Standard) files.

## Usage

Run the application using:

```bash
uv run fcs-plotter
```

To change the plotting backend for better performance with large datasets, edit `config/config.yaml` and set `plotting.backend` to `"pyqtgraph"`.

## Features

- Load and visualize FCS files
- Interactive channel selection for X and Y axes
- Cached file loading for better performance
- Integrated logging display
- Swappable plotting backends (`matplotlib`, `pyqtgraph`) for performance tuning.
