""" The Virus-Total Public API is limited to 500 requests per day and a rate of 4 requests per minute """

# Built-in modules #
import csv
import hashlib
import json
import os
import pickle
import sys
import time
from datetime import datetime

# External modules #
from virus_total_apis import ApiError
from virus_total_apis import PublicApi as VirusTotalPublicApi


# Global variables #
API_KEY = '<Add your API key here>'
INPUT_DIR = 'scanFiles'


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

    # Write the current hour and minute to time CSV file #
    with open(output_csv, 'w') as out_file:
        # Create CSV dict writer object #
        csv_writer = csv.DictWriter(out_file, fieldnames=fields)
        # Write headers (fieldnames) #
        csv_writer.writeheader()
        # Populate the data in fields #
        csv_writer.writerow(time_dict)


"""
########################################################################################################################
Name:       CounterDataOutput
Purpose:    Stores total number of API queries in data file.
Parameters: The data file to store output and the current daily total.
Returns:    None
########################################################################################################################
"""
def CounterDataOutput(output_file: str, day_count: int):
    # Write to counter data file in bytes mode #
    with open(output_file, 'wb') as out_file:
        # Save API int counter to data file #
        pickle.dump(day_count, out_file)


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

    # Read the file storing last execution time #
    with open(input_csv, 'r') as in_file:
        # Read the last execution data #
        csv_data = csv.reader(in_file)

        # Iterate through items in data row #
        for row in csv_data:
            # If empty row or the first row (title)#
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

            try:
                # Ensure input CSV data is int #
                ret_month, ret_day, ret_hour = int(month), int(day), int(hour)
            # If value is not int #
            except ValueError:
                PrintErr('Data Type: Error occurred retrieving CSV execution time values')
                sys.exit(4)

            return ret_month, ret_day, ret_hour


"""
########################################################################################################################
Name:       CounterDataInput
Purpose:    Reads total number of API queries from data file.
Parameters: The data file to read the stored data.
Returns:    The data read from the data file (Daily API query count).
########################################################################################################################
"""
def CounterDataInput(input_file: str) -> int:
    # Read from counter data file in bytes mode #
    with open(input_file, 'rb') as in_file:
        # Load the int API counter #
        stored_counter = pickle.load(in_file)

    return stored_counter


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
Name:       main
Purpose:    Gets files from input dir, iterates over them, sending and retrieving json report of Virus-Total analysis \
            of the item analyzed by the API.
Parameters: None
Returns:    None
########################################################################################################################
"""
def main():
    report_file = 'virus-total_report.txt'
    counter_file = 'counter_data.data'
    execution_time_file = 'last_execution_time.csv'

    # If report file exists but does not have written access #
    if os.path.isfile(report_file) and not os.access(report_file, os.W_OK):
        PrintErr(f'File IO: {report_file} exists and does not have write'
                 ' access, confirm it is closed and try again')
        sys.exit(1)

    # If the counter data file does not exist #
    if not os.path.isfile(counter_file):
        total_count = 0
    # If the data file exists #
    else:
        # If the data file does not have access #
        if not os.access(counter_file, os.R_OK):
            PrintErr(f'File IO: {counter_file} does not have read'
                     ' access, confirm it is closed and try again')
            sys.exit(2)

        # Load the counter data from the data file #
        total_count = CounterDataInput(counter_file)

    # Get the current execution time #
    start_time = datetime.now()
    month, day, hour = start_time.month, start_time.day, start_time.hour

    # If the last execution time file exists #
    if os.path.isfile(execution_time_file):
        # If the last execution time file does not have read/write access #
        if not os.access(execution_time_file, os.R_OK) or not os.access(execution_time_file, os.W_OK):
            PrintErr(f'File IO: {execution_time_file} exists and does not have read/write'
                     ' access, confirm it is closed and try again')
            sys.exit(3)

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

    minute_count = 4
    # Initialize the Virus-Total API object #
    vt_object = VirusTotalPublicApi(API_KEY)

    print(f'Current number of daily Virus-Total API queries: {total_count}\n')
    print(f'Starting Virus-Total file check on file in {INPUT_DIR}')
    print(f'{(44 + len(INPUT_DIR)) * "*"}')
    try:
        # Open report file in append mode #
        with open(report_file, 'a') as out_file:
            # Get the contents of input dir as list #
            for _, _, files in os.walk(INPUT_DIR):
                for file in files:
                    # If the maximum API calls have been used for the day #
                    if total_count == 500:
                        print('Only 500 queries allowed per day .. exiting program')
                        break

                    # If the maximum API calls have been used for the minute #
                    if minute_count == 0:
                        print('Only 4 queries allowed per minute, sleeping 60 seconds')
                        time.sleep(60)
                        minute_count = 4

                    print(f'Generating report for: {file}')
                    bytes_item = file.encode()

                    # Generate MD5 hash of current file in list #
                    file_md5 = hashlib.md5(bytes_item).hexdigest()
                    try:
                        # Get a Virus-Total report of the hashed file #
                        response = vt_object.get_file_report(file_md5)
                    # If error occurs interacting with Virus-Total API #
                    except ApiError as err:
                        PrintErr(f'API error occurred - {err}')
                        sys.exit(5)

                    # If successful response code is returned #
                    if response['response_code'] == 200:
                        # Write the name of the current file to report file #
                        out_file.write(f'File - {file}:\n{(9 + len(file)) * "*"}\n')
                        # Write json results to output report file #
                        json.dump(response, out_file, sort_keys=False, indent=4)
                        out_file.write('\n\n')

                    # If response code is for maximum API calls per minute #
                    elif response['response_code'] == 204:
                        PrintErr('Max API Error: API calls per minute maxed out at 4, wait 60 seconds and try again')
                        sys.exit(6)

                    # If response code is for invalid request #
                    elif response['response_code'] == 400:
                        PrintErr('Request Error: Invalid API request detected, check request formatting')
                        sys.exit(7)

                    # If response code is for forbidden access #
                    elif response['response_code'] == 403:
                        PrintErr('Forbidden Error: Unable to access API, confirm key exists and is valid')
                        sys.exit(8)

                    # If unknown response code occurs #
                    else:
                        PrintErr('Unknown response code occurred')
                        sys.exit(9)

                    total_count += 1
                    minute_count -= 1

    # Ctrl + C to exit #
    except KeyboardInterrupt:
        pass

    # If error occurs writing to report output file #
    except (IOError, OSError) as err:
        PrintErr(f'File IO: Error occurred writing to {report_file} - {err}')
        sys.exit(10)

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

    sys.exit(0)


if __name__ == '__main__':
    main()
