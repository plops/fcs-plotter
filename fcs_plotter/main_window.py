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
    QSpinBox,
    QDoubleSpinBox,
    QHBoxLayout,
)
from PyQt6.QtCore import Qt
from .data_processing import load_fcs_file, load_and_merge_fcs_files
from .config import config
from .plotting.factory import get_plotter, PLOTTER_NAMES

logger = logging.getLogger("fcs_plotter")


class MainWindow(QMainWindow):
    def __init__(self, input_files=None):
        super().__init__()
        self.setWindowTitle("FCS Plotter")
        self.setGeometry(100, 100, 1200, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.datasets = {}  # {file_path: (data, metadata)}
        self.merged_df = None
        self.current_file = None
        self.plotter = None
        self.plot_widget = None

        self._setup_ui()

        if input_files:
            self.load_files(input_files)

    def _setup_ui(self):
        # Top panel for controls
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)

        self.load_button = QPushButton("Load FCS File(s)")
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

        # Plotting parameters
        plot_params_layout = QHBoxLayout()

        # Plotter selection
        self.plotter_label = QLabel("Plotting Library:")
        self.plotter_combo = QComboBox()
        self.plotter_combo.addItems(PLOTTER_NAMES)
        self.plotter_combo.currentTextChanged.connect(self.change_plotter)
        plot_params_layout.addWidget(self.plotter_label)
        plot_params_layout.addWidget(self.plotter_combo)

        # Spot size
        self.spot_size_label = QLabel("Spot Size:")
        self.spot_size_spinbox = QSpinBox()
        self.spot_size_spinbox.setRange(1, 100)
        self.spot_size_spinbox.setValue(config["plotting"]["spot_size"])
        self.spot_size_spinbox.valueChanged.connect(self.plot_data)
        plot_params_layout.addWidget(self.spot_size_label)
        plot_params_layout.addWidget(self.spot_size_spinbox)

        # Spot alpha
        self.spot_alpha_label = QLabel("Spot Alpha:")
        self.spot_alpha_spinbox = QDoubleSpinBox()
        self.spot_alpha_spinbox.setRange(0.01, 1.0)
        self.spot_alpha_spinbox.setSingleStep(0.05)
        self.spot_alpha_spinbox.setValue(config["plotting"]["spot_alpha"])
        self.spot_alpha_spinbox.valueChanged.connect(self.plot_data)
        plot_params_layout.addWidget(self.spot_alpha_label)
        plot_params_layout.addWidget(self.spot_alpha_spinbox)

        # Quantile
        self.quantile_label = QLabel("Quantile:")
        self.quantile_spinbox = QDoubleSpinBox()
        self.quantile_spinbox.setRange(0.01, 1.0)
        self.quantile_spinbox.setSingleStep(0.05)
        self.quantile_spinbox.setValue(config["plotting"]["quantile"])
        self.quantile_spinbox.valueChanged.connect(self.plot_data)
        plot_params_layout.addWidget(self.quantile_label)
        plot_params_layout.addWidget(self.quantile_spinbox)

        # Range Margin
        self.range_margin_label = QLabel("Range Margin:")
        self.range_margin_spinbox = QDoubleSpinBox()
        self.range_margin_spinbox.setRange(0.0, 2.0)
        self.range_margin_spinbox.setSingleStep(0.05)
        self.range_margin_spinbox.setValue(config["plotting"]["range_margin"])
        self.range_margin_spinbox.valueChanged.connect(self.plot_data)
        plot_params_layout.addWidget(self.range_margin_label)
        plot_params_layout.addWidget(self.range_margin_spinbox)

        # Ratio
        self.ratio_label = QLabel("Ratio:")
        self.ratio_spinbox = QDoubleSpinBox()
        self.ratio_spinbox.setRange(0.01, 1.0)
        self.ratio_spinbox.setSingleStep(0.05)
        self.ratio_spinbox.setValue(config["plotting"]["ratio"])
        self.ratio_spinbox.valueChanged.connect(self.plot_data)
        plot_params_layout.addWidget(self.ratio_label)
        plot_params_layout.addWidget(self.ratio_spinbox)

        control_layout.addLayout(plot_params_layout)

        # Main splitter for plot and logs
        self.main_splitter = QSplitter(Qt.Orientation.Vertical)

        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.main_splitter.addWidget(self.log_display)
        self.log_handler = QtLogHandler(self.log_display)
        logger.addHandler(self.log_handler)

        self.layout.addWidget(control_widget)
        self.layout.addWidget(self.main_splitter)

        # Initialize plotter
        plotter_backend = config["plotting"]["backend"]
        if plotter_backend in PLOTTER_NAMES:
            self.plotter_combo.setCurrentText(plotter_backend)
        self.change_plotter(self.plotter_combo.currentText())

    def change_plotter(self, plotter_name):
        if self.plot_widget:
            self.plot_widget.setParent(None)
            self.plot_widget.deleteLater()

        self.plotter = get_plotter(plotter_name)
        self.plot_widget = self.plotter.get_widget()
        self.main_splitter.insertWidget(0, self.plot_widget)
        self.plot_data()

    def load_file(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Open FCS File(s)", "", "FCS Files (*.fcs)"
        )
        if file_paths:
            self.load_files(file_paths)

    def load_files(self, file_paths):
        for file_path in file_paths:
            if file_path not in self.datasets:
                data, metadata = load_fcs_file(file_path)
                if data is not None:
                    self.datasets[file_path] = (data, metadata)

        if self.datasets:
            self.merged_df = load_and_merge_fcs_files(self.datasets)
            self._update_channel_selectors()
            self.plot_data()

    def _update_channel_selectors(self):
        if self.merged_df is not None and not self.merged_df.empty:
            # Get channels from the merged dataframe, excluding 'file_path'
            channels = [col for col in self.merged_df.columns if col != "file_path"]
            current_x = self.x_channel_combo.currentText()
            current_y = self.y_channel_combo.currentText()

            self.x_channel_combo.blockSignals(True)
            self.y_channel_combo.blockSignals(True)

            self.x_channel_combo.clear()
            self.x_channel_combo.addItems(channels)
            self.y_channel_combo.clear()
            self.y_channel_combo.addItems(channels)

            # Restore previous selection if possible
            if current_x in channels:
                self.x_channel_combo.setCurrentText(current_x)
            elif config["plotting"]["default_x_channel"] in channels:
                self.x_channel_combo.setCurrentText(
                    config["plotting"]["default_x_channel"]
                )

            if current_y in channels:
                self.y_channel_combo.setCurrentText(current_y)
            elif config["plotting"]["default_y_channel"] in channels:
                self.y_channel_combo.setCurrentText(
                    config["plotting"]["default_y_channel"]
                )

            self.x_channel_combo.blockSignals(False)
            self.y_channel_combo.blockSignals(False)

    def plot_data(self):
        if self.merged_df is None or self.merged_df.empty or self.plotter is None:
            if self.plotter:
                self.plotter.clear()
            return

        x_channel = self.x_channel_combo.currentText()
        y_channel = self.y_channel_combo.currentText()

        if x_channel and y_channel:
            spot_size = self.spot_size_spinbox.value()
            spot_alpha = self.spot_alpha_spinbox.value()
            quantile = self.quantile_spinbox.value()
            range_margin = self.range_margin_spinbox.value()
            ratio = self.ratio_spinbox.value()

            self.plotter.plot_data(
                self.merged_df,
                x_channel,
                y_channel,
                spot_size,
                spot_alpha,
                quantile,
                range_margin,
                ratio,
            )


class QtLogHandler(logging.Handler):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.append(msg)
