""" The Virus-Total Public API is limited to 500 requests per day and a rate of 4 requests per minute """

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
from Modules.Utils import LoadProgramData, QtError, StoreProgramData
from Modules.VTotal_Scanner import VTotalScan


# Pseudo constants #
API_KEY = '1ffd1ded4a3a59d2fad391427e43c33310eb1de44f8fccfd10406195ae8d028f'
INPUT_DIR = 'VTotalScanDock'

# Global variables #
global total_count


class MainWindow(Qtw.QMainWindow):
    """ Purpose:  Initialize and configure the graphical user interface. """
    """ Parameters:  The main window object of the GUI. """
    """ Returns:  Nothing """
    def __init__(self, result_file: str, daily_calls: int):
        # Set class to inherit attributes of parent class #
        super().__init__()

        self.setStyleSheet('background-color: #1eb300;')

        # Set the title of the application #
        self.setWindowTitle('VTotal PyClient')

        # Set the window size #
        self.setGeometry(0, 0, 800, 600)

        # Total number of daily API calls #
        self.api_count = daily_calls
        # Save the output file name #
        self.out_file = result_file

        # Create a label for instructions #
        self.instruction_label = Qtw.QLabel('Click button below to run Virus Total API'
                                            ' scan on VTotalScanDock contents', self)
        # Position and set label size #
        self.instruction_label.move(0, 0)
        self.instruction_label.resize(700, 100)

        # Set label to word wrap #
        self.instruction_label.setWordWrap(True)
        # Change label font size #
        self.instruction_label.setFont(Qtg.QFont('Arial', 18))
        # Align label center #
        self.instruction_label.setAlignment(Qt.AlignCenter)
        # Set label css border #
        self.instruction_label.setStyleSheet('''
                                               color: #1eb300;
                                               background-color: #000000;
                                               border: 2px solid #1eb300;
                                               border-radius: 10px;
                                             ''')

        # Create label to display current api counter #
        self.counter_label = Qtw.QLabel(f'# of daily API calls\n{self.api_count}', self)
        # Position and set label size #
        self.counter_label.move(700, 0)
        self.counter_label.resize(100, 100)

        # Set label to word wrap #
        self.counter_label.setWordWrap(True)
        # Change label font size #
        self.counter_label.setFont(Qtg.QFont('Arial', 14))
        # Align label center #
        self.counter_label.setAlignment(Qt.AlignCenter)
        # Set label css border #
        self.counter_label.setStyleSheet('''
                                           border: 2px solid #000000;
                                           border-radius: 10px;
                                         ''')

        # Create scan output box #
        self.output_box = Qtw.QTextEdit('', self)
        # Set the console output screen to read-only #
        self.output_box.setReadOnly(True)
        # Position and set output box size #
        self.output_box.move(0, 150)
        self.output_box.resize(800, 350)

        # Change label font size #
        self.output_box.setFont(Qtg.QFont('Arial', 16))
        # Align label left #
        self.output_box.setAlignment(Qt.AlignLeft)
        # Set output box css border #
        self.output_box.setStyleSheet('''
                                        background-color: #ffffff;
                                        border: 2px solid #000000;
                                        border-radius: 10px;
                                      ''')

        # Create button to execute tests #
        self.scan_button = Qtw.QPushButton('Run Scan', self)
        # Position and set button size #
        self.scan_button.move(0, 500)
        self.scan_button.resize(800, 100)
        # Change button font size #
        self.scan_button.setFont(Qtg.QFont('Arial', 18))
        # Set function to execute when pressed #
        self.scan_button.clicked.connect(self.OnPress)
        # Set button css #
        self.scan_button.setStyleSheet('''
                                        QPushButton {
                                            color: #000000;
                                            background-color: #1eb300;
                                            border: 2px solid #000000;
                                            border-radius: 10px;
                                        }
            
                                        QPushButton:hover {
                                            color: #1eb300;
                                            background-color: #000000;
                                            border: 2px solid #1eb300;
                                            border-radius: 10px;
                                        }
                                        ''')

        # Display the app #
        self.show()

    def OnPress(self):
        """ Purpose:  Executes Virus Total scanner function when button is clicked """
        """ Parameters:  Nothing """
        """ Returns:  Nothing """
        global total_count
        print(self.instruction_label.setText('Scan is running .. 4 items are scanned every 60 seconds based on API'
                                             ' limitations. This operation could take some time depending on the'
                                             'the amount of files in the VTotalScanDock'))
        # Call app to process label text change #
        Qtg.QGuiApplication.processEvents()

        # Pass needed params into virus scanner, get the updated daily API call total in return #
        total_count = VTotalScan(API_KEY, INPUT_DIR, self.out_file, self.api_count, self.output_box)

        # Update daily API counter #
        self.counter_label.setText(f'# of daily API calls\n{total_count}')
        # Call app to process counter text change #
        Qtg.QGuiApplication.processEvents()

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

    # Confirm application is scaled to screen resolution #
    os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'

    # Get the current execution time #
    start_time = datetime.now()
    month, day, hour = start_time.month, start_time.day, start_time.hour

    report_file = f'VirusTotalReport_{month}-{day}-{hour}.txt'
    counter_file = 'counter_data.data'
    execution_time_file = 'last_execution_time.csv'

    # Load the program data (API daily call count & exec time of first call) #
    total_count, old_month, old_day, old_hour = LoadProgramData(counter_file, execution_time_file, month, day, hour)

    logging.info(f'Count before app {total_count}\n')

    # Initialize QApplication class #
    app = Qtw.QApplication(sys.argv)
    # Configure the main window UI for app #
    _ = MainWindow(report_file, total_count)

    # Exit application process when closed #
    try:
        sys.exit(app.exec_())

    # Occurs when the user hits the exit button #
    except SystemExit:
        pass

    logging.info(f'Count after app: {total_count}')

    # Store the program data for next execution #
    StoreProgramData(counter_file, total_count, execution_time_file, old_month, old_day, old_hour, day, hour)


if __name__ == "__main__":
    # Initialize logging facilities #
    logging.basicConfig(level=logging.DEBUG, filename='VTotal_GuiLog.log')

    try:
        main()

    # If unknown exception occurs #
    except Exception as err:
        QtError(err)
        logging.exception(f'Unexpected error occurred:  {err}\n\n')
        sys.exit(1)

    sys.exit(0)
