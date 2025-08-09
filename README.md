# FCS Plotter

A PyQt6 application for reading and plotting FCS (Flow Cytometry Standard) files.

## Installation

```bash
# Install in development mode
uv pip install -e .
```

## Usage

Run the application using any of these methods:

```bash
# Using the installed command
fcs-plotter

# Running as a module
uv run python -m fcs_plotter

# Direct execution
uv run python fcs_plotter/main.py
```

## Features

- Load and visualize FCS files
- Interactive channel selection for X and Y axes
- Cached file loading for better performance
- Integrated logging display
