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

        self.file_label = QLabel("Current FCS File:")
        self.file_combo = QComboBox()
        self.file_combo.currentTextChanged.connect(self.file_selection_changed)
        control_layout.addWidget(self.file_label)
        control_layout.addWidget(self.file_combo)

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
                    self.file_combo.addItem(file_path)

        if self.datasets:
            self.merged_df = load_and_merge_fcs_files(self.datasets)
            if self.file_combo.count() > 0 and self.current_file is None:
                self.file_combo.setCurrentIndex(0)
            # self.plot_data() is called by file_selection_changed -> update_channel_selectors -> plot_data
            # but if only one file is loaded, file_selection_changed is not triggered if it's already selected
            # so we might need to call it.
            # The selection change will trigger the rest of the update chain.
            if self.file_combo.currentIndex() == 0:
                self.file_selection_changed(self.file_combo.currentText())

    def file_selection_changed(self, file_path):
        if file_path and file_path in self.datasets:
            self.current_file = file_path
            self.update_channel_selectors()
            self.plot_data()

    def update_channel_selectors(self):
        if self.current_file and self.current_file in self.datasets:
            data, _ = self.datasets[self.current_file]
            channels = data.columns
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
        if self.merged_df is None or self.merged_df.empty or self.plotter is None:
            return

        x_channel = self.x_channel_combo.currentText()
        y_channel = self.y_channel_combo.currentText()

        if x_channel and y_channel:
            spot_size = self.spot_size_spinbox.value()
            spot_alpha = self.spot_alpha_spinbox.value()

            self.plotter.plot_data(
                self.merged_df, x_channel, y_channel, spot_size, spot_alpha
            )


class QtLogHandler(logging.Handler):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.append(msg)
