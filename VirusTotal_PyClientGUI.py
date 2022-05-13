# Built-in modules #
import logging
import os
import sys
from datetime import datetime

# External modules #
from PyQt5.QtCore import Qt
import PyQt5.QtWidgets as Qtw
import PyQt5.QtGui as Qtg

# Custom modules #
from Modules.Utils import CounterDataInput, CounterDataOutput, TimeCsvInput, TimeCsvOutput
from Modules.VTotal_Scanner import VTotalScan


# Pseudo constants #
API_KEY = '< Add API key here >'
INPUT_DIR = 'VTotalScanDock'

# Global variables #
global total_count


class MainWindow(Qtw.QWidget):
    """ Purpose:  Initialize and configure the graphical user interface. """
    """ Parameters:  The main window object of the GUI. """
    """ Returns:  Nothing """
    def __init__(self, result_file: str, daily_calls: int):
        # Set class to inherit attributes of parent class #
        super().__init__()

        # Set the window size #
        self.resize(800, 600)

        # Total number of daily API calls #
        self._api_count = daily_calls
        # Save the output file name #
        self.out_file = result_file

        # Create a label #
        self.instruction_label = Qtw.QLabel('Click button below to run Virus Total API'
                                            ' scan on VTotalScanDock contents')
        # Change label font size #
        self.instruction_label.setFont(Qtg.QFont('Arial', 18))
        # Align label center #
        self.instruction_label.setAlignment(Qt.AlignCenter)

        # Create button to execute tests #
        self.scan_button = Qtw.QPushButton('Run Scan')
        # Change button font size #
        self.scan_button.setFont(Qtg.QFont('Arial', 18))
        # Set function to execute when pressed #
        self.scan_button.clicked.connect(self.OnPress)

        # Set the title of the application #
        self.setWindowTitle('VTotal PyClient')
        # Set a vertical-based app layout #
        self.setLayout(Qtw.QVBoxLayout())

        # Apply label to app #
        self.layout().addWidget(self.instruction_label)
        # Apply button to app #
        self.layout().addWidget(self.scan_button)

    def OnPress(self):
        """ Purpose:  Executes Virus Total scanner function when button is clicked """
        """ Parameters:  Nothing """
        """ Returns:  Nothing """
        global total_count
        print(self.instruction_label.setText('Scan is running .. 4 items are scanned every 60 seconds based on\nAPI'
                                             ' limitations. This operation could take some time depending on the\n'
                                             'the amount of files in the VTotalScanDock'))
        # Call app to process label text change #
        Qtg.QGuiApplication.processEvents()

        # Pass needed params into virus scanner, get the updated daily API call total in return #
        total_count = VTotalScan(API_KEY, INPUT_DIR, self.out_file, self._api_count)

        print(self.instruction_label.setText('Scan is complete .. check directory for report'))


"""
########################################################################################################################
Name:       main
Purpose:    Manages the application initialization, configuration, and exit.
Parameters: Nothing
Returns:    Nothing
########################################################################################################################
"""
def main():
    global total_count
    report_file = 'virus-total_report.txt'
    counter_file = 'counter_data.data'
    execution_time_file = 'last_execution_time.csv'

    # If report file exists but does not have written access #
    if os.path.isfile(report_file) and not os.access(report_file, os.W_OK):
        logging.exception(f'File IO: {report_file} exists and does not have write'
                           ' access, confirm it is closed and try again')
        sys.exit(6)

    # If the counter data file does not exist #
    if not os.path.isfile(counter_file):
        total_count = 0
    # If the data file exists #
    else:
        # If the data file does not have read access #
        if not os.access(counter_file, os.R_OK):
            logging.exception(f'File IO: {counter_file} does not have read'
                               ' access, confirm it is closed and try again')
            sys.exit(7)

        # Load the counter data from the data file #
        total_count = CounterDataInput(counter_file)

    # Get the current execution time #
    start_time = datetime.now()
    month, day, hour = start_time.month, start_time.day, start_time.hour

    # If the last execution time file exists #
    if os.path.isfile(execution_time_file):
        # If the last execution time file does not have read/write access #
        if not os.access(execution_time_file, os.R_OK) or not os.access(execution_time_file, os.W_OK):
            logging.exception(f'File IO: {execution_time_file} exists and does not have read/write'
                               ' access, confirm it is closed and try again')
            sys.exit(8)

        # Read old execution time from csv file #
        old_month, old_day, old_hour = TimeCsvInput(execution_time_file)

        # If the last execution occurred in the same month and
        # maximum queries have been recorded on data file #
        if old_month == month and total_count == 500:
            # If the on the same day or the next day within less-than 24 hours #
            if old_day == day or (old_day == day + 1 and ((old_hour + 24) % 24 >= hour)):
                pass
            # If the data files are no longer needed #
            else:
                # Delete the counter and execution time files #
                os.remove(counter_file)
                os.remove(execution_time_file)
    else:
        old_month, old_day, old_hour = None, None, None

    logging.info(f'Count before app {total_count}\n')

    # Initialize QApplication class #
    app = Qtw.QApplication([])
    # Configure the main window UI for app #
    widget = MainWindow(report_file, total_count)
    # Display the app #
    widget.show()

    # Exit application process when closed #
    try:
        sys.exit(app.exec_())
    except SystemExit:
        print('Closing App Window ..')

    logging.info(f'Count after app: {total_count}')

    # Save daily allowed total counter to data file #
    CounterDataOutput(counter_file, total_count)

    # If the last execution time file exists #
    if os.path.isfile(execution_time_file):
        if old_month and old_day and old_hour and old_month:
            # If the on the same day or the next day within less-than 24 hours #
            if old_day == day or (old_day == day + 1 and ((old_hour + 24) % 24 >= hour)):
                pass
            # If the 24-hour period is over #
            else:
                # Save the execution time to csv #
                TimeCsvOutput(execution_time_file)
    else:
        # Save the execution time to csv #
        TimeCsvOutput(execution_time_file)


if __name__ == "__main__":
    # Initialize logging facilities #
    logging.basicConfig(level=logging.DEBUG, filename='VTotal_GuiLog.log')

    try:
        main()

    # If unknown exception occurs #
    except Exception as err:
        logging.exception(f'Unexpected error occurred:  {err}\n\n')
        sys.exit(1)

    sys.exit(0)
