""" The Virus-Total Public API is limited to 500 requests per day and a rate of 4 requests per minute """

# Built-in modules #
import hashlib
import json
import os
import sys
import time
from datetime import datetime

# External modules #
from virus_total_apis import ApiError
from virus_total_apis import PublicApi as VirusTotalPublicApi

# Custom modules #
from Modules.Utils import CounterDataInput, CounterDataOutput, PrintErr, TimeCsvInput, TimeCsvOutput

# Pseudo constants #
API_KEY = '< Add your API key here >'
INPUT_DIR = 'VTotalScanDock'


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
        sys.exit(6)

    # If the counter data file does not exist #
    if not os.path.isfile(counter_file):
        total_count = 0
    # If the data file exists #
    else:
        # If the data file does not have read access #
        if not os.access(counter_file, os.R_OK):
            PrintErr(f'File IO: {counter_file} does not have read'
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
            PrintErr(f'File IO: {execution_time_file} exists and does not have read/write'
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
                    # Skip the .keep file #
                    if file.startswith('.'):
                        continue

                    # If the maximum API calls have been used for the day #
                    if total_count == 500:
                        print('Only 500 queries allowed per day .. exiting program')
                        break

                    # If the maximum API calls have been used for the minute #
                    if minute_count == 0:
                        print('Only 4 queries allowed per minute, sleeping 60 seconds\n')
                        time.sleep(60)
                        minute_count = 4

                    print(f'Generating report for: {file}')
                    bytes_item = file.encode()

                    # Generate MD5 hash of current file in list #
                    file_md5 = hashlib.sha256(bytes_item).hexdigest()
                    try:
                        # Get a Virus-Total report of the hashed file #
                        response = vt_object.get_file_report(file_md5)
                    # If error occurs interacting with Virus-Total API #
                    except ApiError as err:
                        PrintErr(f'API error occurred - {err}')
                        sys.exit(9)

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
                        sys.exit(10)

                    # If response code is for invalid request #
                    elif response['response_code'] == 400:
                        PrintErr('Request Error: Invalid API request detected, check request formatting')
                        sys.exit(11)

                    # If response code is for forbidden access #
                    elif response['response_code'] == 403:
                        PrintErr('Forbidden Error: Unable to access API, confirm key exists and is valid')
                        sys.exit(12)

                    # If unknown response code occurs #
                    else:
                        PrintErr('Unknown response code occurred')
                        sys.exit(13)

                    total_count += 1
                    minute_count -= 1

    # Ctrl + C to exit #
    except KeyboardInterrupt:
        pass

    # If error occurs writing to report output file #
    except IOError as err:
        PrintErr(f'File IO: Error occurred writing to {report_file} - {err}')
        sys.exit(14)

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


if __name__ == '__main__':
    try:
        main()

    # If unexpected exception occurs #
    except Exception as e:
        PrintErr(f'Unexpected error occurred - {e}')
        sys.exit(1)

    sys.exit(0)
