# pylint: disable=E0611,I1101
"""
Virus-Total Public API limits 500 requests per day at a rate of 4 requests per minute

Built-in modules
"""
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
# External modules #
from PyQt5.QtCore import Qt
import PyQt5.QtWidgets as Qtw
import PyQt5.QtGui as Qtg
# Custom modules #
from Modules.utils import load_data, qt_err, store_data, TimeTracker
from Modules.vtotal_scanner import vtotal_scan


# Global variables #
API_KEY = os.environ.get('VTOTAL_API_KEY')
global TOTAL_COUNT


class MainWindow(Qtw.QWidget):
    """ Class inherits the attributes of PyQT QMainWindow parent class. """
    def __init__(self, time_instance: object, daily_calls: int):
        """
        Initialize and configure the graphical user interface.

        :param daily_calls:  The current number of API calls that have been executed within the \
                             past day.
        """
        # Set class to inherit attributes of parent class #
        super().__init__()
        # Set the background color of main window #
        self.setStyleSheet('background-color: #1eb300;')
        # Set the title of the application #
        self.setWindowTitle('VTotal PyClient')
        # Set the window size #
        self.setGeometry(0, 0, 800, 600)
        # Initialize grid layout instance #
        __layout = Qtw.QGridLayout()

        # Total number of daily API calls #
        self._api_count = daily_calls
        # Save the path to current working directory #
        self._cwd = cwd
        # Save the program time instance #
        self._time_obj = time_instance

        # Create a label for instructions #
        self._instruction_label = Qtw.QLabel('Click button below to run Virus Total API'
                                            ' scan on VTotalScanDock contents', self)
        # Set label to word wrap #
        self._instruction_label.setWordWrap(True)
        # Change label font size #
        self._instruction_label.setFont(Qtg.QFont('Arial', 16))
        # Align label center #
        self._instruction_label.setAlignment(Qt.AlignCenter)
        # Set label css border #
        self._instruction_label.setStyleSheet('''
            color: #1eb300;
            background-color: #000000;
            border: 10px double #fff633;
            border-radius: 20px;
        ''')
        # Add instruction label box to layout #
        __layout.addWidget(self._instruction_label, 0, 0, 1, 3)

        # Create label to display current api counter #
        self._counter_label = Qtw.QLabel(f'# of daily API calls\n{self._api_count}', self)
        # Set label to word wrap #
        self._counter_label.setWordWrap(True)
        # Change label font size #
        self._counter_label.setFont(Qtg.QFont('Arial', 16))
        # Align label center #
        self._counter_label.setAlignment(Qt.AlignCenter)
        # Set label css border #
        self._counter_label.setStyleSheet('''
            background-color: #ffffff;
            border: 2px solid #000000;
            border-radius: 20px;
        ''')
        # Add counter label box to layout #
        __layout.addWidget(self._counter_label, 0, 3)

        # Create scan output box #
        self._output_box = Qtw.QTextEdit('', self)
        # Set the console output screen to read-only #
        self._output_box.setReadOnly(True)
        # Change label font size #
        self._output_box.setFont(Qtg.QFont('Arial', 16))
        # Align label left #
        self._output_box.setAlignment(Qt.AlignLeft)
        # Set output box css border #
        self._output_box.setStyleSheet('''
            background-color: #ffffff;
            border: 2px solid #000000;
            border-radius: 20px;
        ''')
        # Add output box to layout #
        __layout.addWidget(self._output_box, 1, 0, 4, 4)

        # Create button to execute tests #
        self._scan_button = Qtw.QPushButton('Run Scan', self)
        # Change button font size #
        self._scan_button.setFont(Qtg.QFont('Arial', 20))
        # Set the scan button minimum height #
        self._scan_button.setMinimumHeight(60)
        # Set function to execute when pressed #
        self._scan_button.clicked.connect(self.on_press)
        # Set button css #
        self._scan_button.setStyleSheet('''
            QPushButton {
                color: #000000;
                background-color: #ffffff;
                border: 2px solid #000000;
            }

            QPushButton:hover {
                color: #1eb300;
                background-color: #000000;
                border: 10px double #fff663;
            }
        ''')
        # Add scan button box to layout #
        __layout.addWidget(self._scan_button, 5, 0, 1, 4)
        # Establish GUI layout #
        self.setLayout(__layout)

    def on_press(self):
        """
        Executes Virus Total scanner function when button is clicked.

        :return:  Nothing
        """
        global TOTAL_COUNT
        print(self._instruction_label.setText('Scan is running .. 4 items are scanned every 60 '
                                             'seconds based on API limitations. This operation '
                                             'could take some time depending on the amount of '
                                             'files in the VTotalScanDock'))
        # Call app to process label text change #
        Qtg.QGuiApplication.processEvents()

        # Pass needed params into virus scanner, get the updated daily API call total in return #
        TOTAL_COUNT = vtotal_scan(API_KEY, INPUT_DIR, self._cwd, self._time_obj,
                                  self._api_count, self._output_box)

        # Update daily API counter #
        self._counter_label.setText(f'# of daily API calls\n{TOTAL_COUNT}')
        # Call app to process counter text change #
        Qtg.QGuiApplication.processEvents()

        print(self._instruction_label.setText('Scan is complete .. check directory for report'))


def main():
    """
    Manages the application initialization, configuration, and exit.

    :return:  Nothing
    """
    global TOTAL_COUNT

    # Initialize time tracking instance #
    time_obj = TimeTracker()

    # Confirm application is scaled to screen resolution #
    os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
    os.environ['QT_SCREEN_SCALE_FACTORS'] = '1'
    os.environ['QT_SCALE_FACTOR'] = '1'

    # Get the current execution time #
    start_time = datetime.now()
    time_obj.month, time_obj.day, time_obj.hour = start_time.month, start_time.day, start_time.hour

    counter_file = cwd / 'counter_data.data'
    execution_time_file = cwd / 'last_execution_time.csv'

    # Load the program data (API daily call count & exec time of first call) #
    TOTAL_COUNT, time_obj.old_month, \
    time_obj.old_day, time_obj.old_hour = load_data(counter_file, execution_time_file, time_obj)

    logging.info('Count before app %s', TOTAL_COUNT)

    # Initialize QApplication class #
    app = Qtw.QApplication(sys.argv)
    # Configure the main window UI for app #
    gui = MainWindow(time_obj, TOTAL_COUNT)

    # Exit application process when closed #
    try:
        # Show the application GUI #
        gui.show()
        sys.exit(app.exec_())

    # Occurs when the user hits the exit button #
    except SystemExit:
        pass

    logging.info('Count after app: %s', TOTAL_COUNT)

    # Store the program data for next execution #
    store_data(counter_file, TOTAL_COUNT, execution_time_file, time_obj)


if __name__ == "__main__":
    # Set program file paths #
    cwd = Path.cwd()
    INPUT_DIR = cwd / 'VTotalScanDock'
    # Set the log file name #
    logging.basicConfig(filename='VTotal_GUI_Log.log',
                        format='%(asctime)s %(lineno)4d@%(filename)-24s[%(levelname)s]>>  '
                               ' %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    try:
        main()

    # If unknown exception occurs #
    except Exception as err:
        # Display error on app and log #
        qt_err(err)
        logging.exception('Unexpected error occurred:  %s', err)
        sys.exit(1)

    sys.exit(0)
