# pylint: disable=W0106,I1101
""" Built-in modules """
import csv
import errno
import hashlib
import logging
import os
import pickle
import sys
from datetime import datetime
# External Modules #
import PyQt5.QtWidgets as Qtw
from virus_total_apis import ApiError


def counter_data_input(input_file: str) -> int:
    """
    Reads total number of API queries from data file.

    :param input_file:  The data file to read the stored data.
    :return:  The data read from the data file (daily API query count).
    """
    try:
        # Read from counter data file in bytes mode #
        with open(input_file, 'rb') as in_file:
            # Load the int API counter #
            stored_counter = pickle.load(in_file)

    # If file IO error occurs #
    except (IOError, OSError) as file_err:
        # Lookup, display, and log IO error #
        error_query(input_file, 'rb', file_err)

    return stored_counter


def counter_data_output(output_file: str, day_count: int):
    """
    Stores total number of API queries in data file.

    :param output_file:  The data file where the number of daily API calls will be stored.
    :param day_count:  The current number of API calls withing the last 24-hour period.
    :return:  Nothing
    """
    try:
        # Write to counter data file in bytes mode #
        with open(output_file, 'wb') as out_file:
            # Save API int counter to data file #
            pickle.dump(day_count, out_file)

    # If file IO error occurs #
    except (IOError, OSError) as file_err:
        # Lookup, display, and log IO error #
        error_query(output_file, 'wb', file_err)


def error_query(err_path: str, err_mode: str, err_obj):
    """
    Looks up the errno message to get description.

    :param err_path:  Path to file where error message occurred.
    :param err_mode:  File mode in which error message occurred.
    :param err_obj:  Error message instance.
    :return:  Nothing
    """
    # If file does not exist #
    if err_obj.errno == errno.ENOENT:
        # Print error and log #
        print_err(f'{err_path} does not exist')
        logging.exception('%s does not exist\n\n', err_path)
        sys.exit(2)

    # If the file does not have read/write access #
    elif err_obj.errno == errno.EPERM:
        # Print error and log #
        print_err(f'{err_path} does not have permissions for {err_mode}'
                  ' file mode, if file exists confirm it is closed')
        logging.exception('%s does not have permissions for %s file mode\n\n', err_path, err_mode)
        sys.exit(3)

    # File IO error occurred #
    elif err_obj.errno == errno.EIO:
        # Print error and log #
        print_err(f'IO error occurred during {err_mode} mode on {err_path}')
        logging.exception('IO error occurred during %s mode on %s\n\n', err_mode, err_path)
        sys.exit(4)

    # If other unexpected file operation occurs #
    else:
        # Print error and log #
        print_err(f'Unexpected file operation occurred accessing {err_path}: {err_obj.errno}')
        logging.exception('Unexpected file operation occurred accessing %s: %s\n\n',
                          err_path, err_obj.errno)
        sys.exit(5)


def get_files(path: str):
    """
    Iterate through files in path and add to list if not the .keep file or not a directory.

    :param path:  The path to the dir to iterate through files and add to list.
    :return:  The populated file list.
    """
    file_list = []
    # Append items in path to the file list if they are not .keep or a directory #
    [file_list.append(file.name) for file in os.scandir(path) if not file.name == '.keep' and
     not os.path.isdir(f'{path}{file.name}')]
    return file_list


def hash_send(file_name: str, vt_instance: object) -> dict:
    """
    Encode passed in file as bytes, perform SHA512 hash, and send hash to Virus Total API. Return \
    the result dictionary.

    :param file_name:  The file to be hashed and tested with the Virus Total API.
    :param vt_instance:  The initalized Virus Total instance.
    :return:  The result dictionary of API call.
    """
    # Get file content in bytes form for hashing #
    bytes_item = file_name.encode()
    # Generate SHA256 hash of current file in list #
    file_md5 = hashlib.sha256(bytes_item).hexdigest()

    try:
        # Get a Virus-Total report of the hashed file #
        response = vt_instance.get_file_report(file_md5)

    # If error occurs interacting with Virus-Total API #
    except ApiError as api_err:
        print_err(f'API error occurred - {api_err}')
        logging.exception('Error occurred accessing API: %s\n\n', api_err)
        sys.exit(7)

    return response


def load_data(count_file: str, exec_time_file: str, time_inst: object) -> tuple:
    """
    Checks if exist program data exists. If so, the data loaded from the files and checked to see \
    if the 24-hour period for the 500 daily API calls is past. If it is past the 24-hour period \
    the data files will be deleted to keep track of the new 24 period.

    :param count_file:  Path to the data file containing the current daily API count.
    :param exec_time_file:  Path to the csv file containing program execution time.
    :param time_inst:  Time instance containing current and previous execution time data.
    :return:  Tuple with the start execution time of period and total daily API call count if \
              successful, otherwise None values.
    """
    # If the counter data file does not exist #
    if not os.path.isfile(count_file):
        daily_count = 0
    # If the data file exists #
    else:
        # Load the counter data from the data file #
        daily_count = counter_data_input(count_file)

    # If the last execution time file exists #
    if os.path.isfile(exec_time_file):
        # Read old execution time from csv file #
        prev_month, prev_day, prev_hour = time_csv_input(exec_time_file)

        # If the last execution occurred in the same month and
        # maximum queries have been recorded on data file #
        if prev_month == time_inst.month and daily_count == 500:
            # If the on the same day or the next day within less-than 24 hours #
            if prev_day == time_inst.day or (prev_day == time_inst.day + 1
            and ((prev_hour + 24) % 24 >= time_inst.hour)):
                pass
            # If the data files are no longer needed #
            else:
                # Delete the counter and execution time files #
                os.remove(count_file)
                os.remove(exec_time_file)

        return daily_count, prev_month, prev_day, prev_hour

    return daily_count, None, None, None


def print_err(msg: str):
    """
    Displays error message via standard error.

    :param msg:  The error message to be displayed.
    :return:  Nothing
    """
    print(f'\n* [ERROR] {msg} *\n', file=sys.stderr)


def qt_err(err_obj):
    """
    Prints a GUI error message with PyQT.

    :param err_obj:  Error message instance.
    :return:  Nothing
    """
    msg = Qtw.QMessageBox()
    msg.setIcon(Qtw.QMessageBox.Critical)
    msg.setText("* [ERROR] *")
    msg.setInformativeText(err_obj)
    msg.setWindowTitle("Error")
    msg.exec_()


def store_data(counter_file: str, total_count: int, execution_time_file: str, time_inst: object):
    """
    Stores the API daily API counter data and execution time if first call within a 24-hour period.

    :param counter_file:  Counter data file name.
    :param total_count:  Current number of daily API calls in last 24 hours.
    :param execution_time_file:  Path to csv file where execution time data is stored.
    :param time_inst:  Time instance containing current and previous execution time data.
    :return:  Nothing
    """
    # Save daily allowed total counter to data file #
    counter_data_output(counter_file, total_count)

    # If the last execution time file exists #
    if os.path.isfile(execution_time_file):
        if time_inst.old_month and time_inst.old_day and time_inst.old_hour:
            # If the on the same day or the next day within less-than 24 hours #
            if time_inst.old_day == time_inst.day or (time_inst.old_day == time_inst.day + 1
            and ((time_inst.old_hour + 24) % 24 >= time_inst.hour)):
                pass
            # If the 24-hour period is over #
            else:
                # Save the execution time to csv #
                time_csv_output(execution_time_file)
    else:
        # Save the execution time to csv #
        time_csv_output(execution_time_file)


def time_csv_input(input_csv: str) -> tuple:
    """
    Reads the time data stored in csv file.

    :param input_csv:  The data csv file to read the stored execution time.
    :return:  The stored execution time in csv file (month, day, hour).
    """
    headers = ['month', 'day', 'hour']
    try:
        # Read the file storing last execution time #
        with open(input_csv, 'r', encoding='utf-8', newline='') as in_file:
            # Read the last execution data #
            csv_data = csv.DictReader(in_file, fieldnames=headers)

            # Get last execution time in dict format #
            for row in csv_data:
                month = row['month']
                day = row['day']
                hour = row['hour']
                break

    # If file IO error occurs #
    except (IOError, OSError) as file_err:
        # Lookup, display, and log IO error #
        error_query(input_csv, 'r', file_err)

    try:
        # Ensure input CSV data is int #
        ret_month, ret_day, ret_hour = int(month), int(day), int(hour)

    # If value is not int #
    except ValueError as val_err:
        # Print error and log #
        print_err(f'Value: Error occurred retrieving CSV execution time values - {val_err}')
        logging.exception('Value error occurred converting read csv time data: %s\n\n', val_err)
        sys.exit(6)

    return ret_month, ret_day, ret_hour


def time_csv_output(output_csv: str):
    """
    Stores execution time and data in cvs file.

    :param output_csv:  The data csv file to store execution time output.
    :return:  Nothing
    """
    # Get the current time #
    finish_time = datetime.now()
    # Store time in list #
    time_dict = [finish_time.month, finish_time.day, finish_time.hour]

    try:
        # Write the current hour and minute to time CSV file #
        with open(output_csv, 'w', encoding='utf-8', newline='') as out_file:
            # Create CSV dict writer object #
            csv_writer = csv.writer(out_file)
            # Populate the data in fields #
            csv_writer.writerow(time_dict)

    # If file IO error occurs #
    except (IOError, OSError) as file_err:
        # Lookup, display, and log IO error #
        error_query(output_csv, 'w', file_err)


class TimeTracker:
    """ Class to group the stored and current execution times. """
    old_month = None
    old_day = None
    old_hour = None
    month = None
    day = None
    hour = None
