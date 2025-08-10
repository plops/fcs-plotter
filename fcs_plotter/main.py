import sys
import glob
from PyQt6.QtWidgets import QApplication
from .main_window import MainWindow
from .logger_setup import logger
from .config import config


def main():
    """Main function to run the application."""
    logger.info("Starting FCS Plotter application")
    app = QApplication(sys.argv)

    input_files = []
    if "input_files" in config and config["input_files"]:
        patterns = config["input_files"]
        if isinstance(patterns, str):
            patterns = [patterns]

        for pattern in patterns:
            input_files.extend(glob.glob(pattern, recursive=True))

    main_win = MainWindow(input_files=input_files)
    main_win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
