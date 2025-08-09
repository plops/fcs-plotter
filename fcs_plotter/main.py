import sys
from PyQt6.QtWidgets import QApplication
from .main_window import MainWindow
from .logger_setup import logger


def main():
    """Main function to run the application."""
    logger.info("Starting FCS Plotter application")
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
