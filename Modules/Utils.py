# Built-in modules #
import csv
import errno
import logging
import os
import pickle
import sys
from datetime import datetime

# External Modules #
import PyQt5.QtWidgets as Qtw


"""
################
Function Index #
########################################################################################################################
CounterDataInput - Reads total number of API queries from data file. 
CounterDataOutput - Stores total number of API queries in data file.
ErrorQuery - Looks up the errno message to get description.
LoadProgramData - Checks if exist program data exists. If so, the data loaded from the files and checked to see if the 
                  24 hour period for the 500 daily API calls is past. If it is past the 24 hour period the data files \
                  will be deleted to keep track of the new 24 period.
PrintErr - Displays error message through standard output.
QtError - Prints a GUI error message with PyQT.
TimeCsvInput - Reads the time data stored in CSV file.
TimeCsvOutput - Stores execution time and data in cvs file.
########################################################################################################################
"""


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
Returns:    Nothing
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
Name:       LoadProgramData
Purpose:    Checks if exist program data exists. If so, the data loaded from the files and checked to see if the 24 \
            hour period for the 500 daily API calls is past. If it is past the 24 hour period the data files will be \
            deleted to keep track of the new 24 period.
Parameters: Nothing
Returns:    Tuple with the start execution time of period and total daily API calll count if successfull, otherwise \
            None values. 
########################################################################################################################
"""
def LoadProgramData(count_file: str, exec_time_file: str, month: int, day: int, hour: int) -> tuple:
    # If the counter data file does not exist #
    if not os.path.isfile(count_file):
        daily_count = 0
    # If the data file exists #
    else:
        # Load the counter data from the data file #
        daily_count = CounterDataInput(count_file)

    # If the last execution time file exists #
    if os.path.isfile(exec_time_file):
        # Read old execution time from csv file #
        prev_month, prev_day, prev_hour = TimeCsvInput(exec_time_file)

        # If the last execution occurred in the same month and
        # maximum queries have been recorded on data file #
        if prev_month == month and daily_count == 500:
            # If the on the same day or the next day within less-than 24 hours #
            if prev_day == day or (prev_day == day + 1 and ((prev_hour + 24) % 24 >= hour)):
                pass
            # If the data files are no longer needed #
            else:
                # Delete the counter and execution time files #
                os.remove(count_file)
                os.remove(exec_time_file)

        return daily_count, prev_month, prev_day, prev_hour
    else:
        return daily_count, None, None, None


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
Returns:    Nothing 
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
Name:       StoreProgramData
Purpose:    Stores the API daily API counter data and execution time if first call within a 24 hour period.
Parameters: Counter data file name, current daily API call total, execution time file name, the stored month, day, and \
            hour, and the current day and hour.
Returns:    Nothing
########################################################################################################################
"""
def StoreProgramData(counter_file: str, total_count: int, execution_time_file: str, old_month: int, old_day: int,
                     old_hour: int, day: int, hour: int):
    # Save daily allowed total counter to data file #
    CounterDataOutput(counter_file, total_count)

    # If the last execution time file exists #
    if os.path.isfile(execution_time_file):
        if old_month and old_day and old_hour:
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
        sys.exit(6)

    return ret_month, ret_day, ret_hour


"""
########################################################################################################################
Name:       TimeCsvOutput
Purpose:    Stores execution time and data in cvs file.
Parameters: The data file to store output.
Returns:    Nothing
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
