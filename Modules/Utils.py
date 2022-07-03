# Built-in modules #
import csv
import errno
import logging
import pickle
import sys
from datetime import datetime

# External Modules #
import PyQt5.QtWidgets as Qtw

"""
########################################################################################################################
Name:       CounterDataInput
Purpose:    Reads total number of API queries from data file.
Parameters: The data file to read the stored data.
Returns:    The data read from the data file (Daily API query count).
########################################################################################################################
"""
def CounterDataInput(input_file: str) -> int:
    try:
        # Read from counter data file in bytes mode #
        with open(input_file, 'rb') as in_file:
            # Load the int API counter #
            stored_counter = pickle.load(in_file)

    # If file IO error occurs #
    except IOError as err:
        ErrorQuery(input_file, 'rb', err)

    return stored_counter


"""
########################################################################################################################
Name:       CounterDataOutput
Purpose:    Stores total number of API queries in data file.
Parameters: The data file to store output and the current daily total.
Returns:    None
########################################################################################################################
"""
def CounterDataOutput(output_file: str, day_count: int):
    try:
        # Write to counter data file in bytes mode #
        with open(output_file, 'wb') as out_file:
            # Save API int counter to data file #
            pickle.dump(day_count, out_file)

    # If file IO error occurs #
    except IOError as err:
        ErrorQuery(output_file, 'wb', err)


"""
########################################################################################################################
Name:       ErrorQuery
Purpose:    Looks up the errno message to get description.
Parameters: Errno message.
Returns:    Nothing
########################################################################################################################
"""
def ErrorQuery(err_path: str, err_mode: str, err_obj):
    # If file does not exist #
    if err_obj.errno == errno.ENOENT:
        PrintErr(f'{err_path} does not exist')
        logging.exception(f'{err_path} does not exist\n\n')
        sys.exit(2)

    # If the file does not have read/write access #
    elif err_obj.errno == errno.EPERM:
        PrintErr(f'{err_path} does not have permissions for {err_mode} file mode, if file exists confirm it is closed')
        logging.exception(f'{err_path} does not have permissions for {err_mode} file mode\n\n')
        sys.exit(3)

    # File IO error occurred #
    elif err_obj.errno == errno.EIO:
        PrintErr(f'IO error occurred during {err_mode} mode on {err_path}')
        logging.exception(f'IO error occurred during {err_mode} mode on {err_path}\n\n')
        sys.exit(4)

    # If other unexpected file operation occurs #
    else:
        PrintErr(f'Unexpected file operation occurred accessing {err_path}: {err_obj.errno}')
        logging.exception(f'Unexpected file operation occurred accessing {err_path}: {err_obj.errno}\n\n')
        sys.exit(5)


"""
########################################################################################################################
Name:       PrintErr
Purpose:    Displays error message through standard output.
Parameters: Error message to be displayed.
Returns:    None
########################################################################################################################
"""
def PrintErr(msg: str):
    print(f'\n* [ERROR] {msg} *\n', file=sys.stderr)


"""
########################################################################################################################
Name:       QtError
Purpose:    Prints a GUI error message with PyQT.
Parameters: Error message object.
Returns:    
########################################################################################################################
"""
def QtError(err_obj: object):
    msg = Qtw.QMessageBox()
    msg.setIcon(Qtw.QMessageBox.Critical)
    msg.setText("* [ERROR] *")
    msg.setInformativeText(err_obj)
    msg.setWindowTitle("Error")
    msg.exec_()


"""
########################################################################################################################
Name:       TimeCsvInput
Purpose:    Reads the time data stored in CSV file.
Parameters: The data file to read the stored data.
Returns:    The data read from the CSV file (Month, Day, Hour).
########################################################################################################################
"""
def TimeCsvInput(input_csv: str) -> tuple:
    title_row = True
    count = 0

    try:
        # Read the file storing last execution time #
        with open(input_csv, 'r') as in_file:
            # Read the last execution data #
            csv_data = csv.reader(in_file)

            # Iterate through items in data row #
            for row in csv_data:
                # If empty row or the first row (title) #
                if not row or title_row:
                    if title_row:
                        title_row = False

                    continue

                # Iterate through CSV row #
                for item in row:
                    if count == 0:
                        month = item
                    elif count == 1:
                        day = item
                    elif count == 2:
                        hour = item
                    else:
                        break

                    count += 1

    # If file IO error occurs #
    except IOError as err:
        # Lookup, display, and log IO error #
        ErrorQuery(input_csv, 'r', err)

    try:
        # Ensure input CSV data is int #
        ret_month, ret_day, ret_hour = int(month), int(day), int(hour)

    # If value is not int #
    except ValueError as err:
        PrintErr(f'Value: Error occurred retrieving CSV execution time values - {err}')
        sys.exit(4)

    return ret_month, ret_day, ret_hour


"""
########################################################################################################################
Name:       TimeCsvOutput
Purpose:    Stores execution time and data in cvs file.
Parameters: The data file to store output.
Returns:    None
########################################################################################################################
"""
def TimeCsvOutput(output_csv: str):
    # CSV field names #
    fields = ['Month', 'Day', 'Hour']
    # Get the current time #
    finish_time = datetime.now()
    # Store time in dict #
    time_dict = {'Month': finish_time.month, 'Day': finish_time.day, 'Hour': finish_time.hour}

    try:
        # Write the current hour and minute to time CSV file #
        with open(output_csv, 'w') as out_file:
            # Create CSV dict writer object #
            csv_writer = csv.DictWriter(out_file, fieldnames=fields)
            # Write headers (fieldnames) #
            csv_writer.writeheader()
            # Populate the data in fields #
            csv_writer.writerow(time_dict)

    # If file IO error occurs #
    except IOError as err:
        # Lookup, display, and log IO error #
        ErrorQuery(output_csv, 'w', err)
