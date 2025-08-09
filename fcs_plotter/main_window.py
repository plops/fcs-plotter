import logging
from PyQt6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QFileDialog,
    QComboBox,
    QLabel,
    QSplitter,
    QTextEdit,
)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from .data_processing import load_fcs_file
from .config import config

logger = logging.getLogger("fcs_plotter")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FCS Plotter")
        self.setGeometry(100, 100, 1200, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.data = None
        self.metadata = None

        self._setup_ui()

    def _setup_ui(self):
        # Top panel for controls
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)

        self.load_button = QPushButton("Load FCS File")
        self.load_button.clicked.connect(self.load_file)
        control_layout.addWidget(self.load_button)

        self.x_channel_label = QLabel("X-Axis Channel:")
        self.x_channel_combo = QComboBox()
        self.x_channel_combo.currentTextChanged.connect(self.plot_data)
        control_layout.addWidget(self.x_channel_label)
        control_layout.addWidget(self.x_channel_combo)

        self.y_channel_label = QLabel("Y-Axis Channel:")
        self.y_channel_combo = QComboBox()
        self.y_channel_combo.currentTextChanged.connect(self.plot_data)
        control_layout.addWidget(self.y_channel_label)
        control_layout.addWidget(self.y_channel_combo)

        # Main splitter for plot and logs
        main_splitter = QSplitter(Qt.Orientation.Vertical)

        # Matplotlib plot canvas
        self.plot_canvas = FigureCanvas(Figure(figsize=(5, 4)))
        self.plot_ax = self.plot_canvas.figure.subplots()
        main_splitter.addWidget(self.plot_canvas)

        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        main_splitter.addWidget(self.log_display)
        self.log_handler = QtLogHandler(self.log_display)
        logger.addHandler(self.log_handler)

        self.layout.addWidget(control_widget)
        self.layout.addWidget(main_splitter)

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open FCS File", "", "FCS Files (*.fcs)"
        )
        if file_path:
            self.data, self.metadata = load_fcs_file(file_path)
            if self.data is not None:
                self.update_channel_selectors()
                self.plot_data()

    def update_channel_selectors(self):
        if self.data is not None:
            channels = self.data.columns
            self.x_channel_combo.clear()
            self.x_channel_combo.addItems(channels)
            self.y_channel_combo.clear()
            self.y_channel_combo.addItems(channels)

            # Set default channels from config
            default_x = config["plotting"]["default_x_channel"]
            default_y = config["plotting"]["default_y_channel"]
            if default_x in channels:
                self.x_channel_combo.setCurrentText(default_x)
            if default_y in channels:
                self.y_channel_combo.setCurrentText(default_y)

    def plot_data(self):
        if self.data is not None:
            x_channel = self.x_channel_combo.currentText()
            y_channel = self.y_channel_combo.currentText()

            if x_channel and y_channel:
                self.plot_ax.clear()
                self.plot_ax.scatter(
                    self.data[x_channel], self.data[y_channel], alpha=0.5, s=5
                )
                self.plot_ax.set_xlabel(x_channel)
                self.plot_ax.set_ylabel(y_channel)
                self.plot_ax.set_title(f"{y_channel} vs {x_channel}")
                self.plot_ax.grid(True)
                self.plot_canvas.draw()
                logger.info(f"Plotted {y_channel} vs {x_channel}")


class QtLogHandler(logging.Handler):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.append(msg)
