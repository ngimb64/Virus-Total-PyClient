# pylint: disable=E0401
"""
Virus-Total Public API limits 500 requests per day at a rate of 4 requests per minute

Built-in modules
"""
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
# External modules #
from virus_total_apis import PublicApi as VirusTotalPublicApi
# Custom modules #
from Modules.utils import error_query, get_files, hash_send, load_data, print_err, store_data, \
                          TimeTracker


# Pseudo constants #
API_KEY = os.environ.get('VTOTAL_API_KEY')


def main():
    """
    Gets files from input dir, iterates over them, sending and retrieving json report of \
    Virus-Total analysis of the item analyzed by the API.

    :return:  Nothing
    """
    # Initialize time tracking instance #
    time_obj = TimeTracker()
    # Get the current execution time #
    start_time = datetime.now()
    time_obj.month, time_obj.day, time_obj.hour = start_time.month, start_time.day, start_time.hour
    # Set the counter file and execution time file paths #
    counter_file = cwd / 'counter_data.data'
    execution_time_file = cwd / 'last_execution_time.csv'

    # Load the program data (API daily call count & exec time of first call) #
    total_count, time_obj.old_month, \
    time_obj.old_day, time_obj.old_hour = load_data(counter_file, execution_time_file, time_obj)

    # Initialize the Virus-Total API object #
    vt_object = VirusTotalPublicApi(API_KEY)
    minute_count = 4

    # Get list of files to be scanned #
    files = get_files(input_dir)

    print('''
 _   ___                ______     __       __  ___       ________          __ 
| | / (_)_____ _____   /_  __/__  / /____ _/ / / _ \\__ __/ ___/ (_)__ ___  / /_
| |/ / / __/ // (_-<    / / / _ \\/ __/ _ `/ / / ___/ // / /__/ / / -_) _ \\/ __/
|___/_/_/  \\_,_/___/   /_/  \\___/\\__/\\_,_/_/ /_/   \\_, /\\___/_/_/\\__/_//_/\\__/ 
                                                  /___/
''')
    print(f'Current number of daily Virus-Total API queries: {total_count}\n')
    print(f'Starting Virus-Total file check on file in {input_dir.name}')
    print(f'{(44 + len(input_dir.name)) * "*"}')

    # Iterate through gathered file list #
    for file in files:
        # Format report file path #
        report_file = cwd / f'{file.name}_{time_obj.month}-{time_obj.day}-{time_obj.hour}.txt'
        try:
            # Open report file in append mode #
            with report_file.open('a', encoding='utf-8') as out_file:
                # If the maximum API calls have been used for the day #
                if total_count == 500:
                    print_err('\nOnly 500 queries allowed per day .. exiting program')
                    break

                # If the maximum API calls have been used for the minute #
                if minute_count == 0:
                    print('\nOnly 4 queries allowed per minute, sleeping 60 seconds\n')
                    time.sleep(60)
                    minute_count = 4

                print(f'Generating report for: {file.name}')

                # Hash file and send report, return response #
                response = hash_send(file, vt_object)

                # If successful response code is returned #
                if response['response_code'] == 200:
                    # Write the name of the current file to report file #
                    out_file.write(f'File - {file.name}:\n{(9 + len(file.name)) * "*"}\n')
                    # Write json results to output report file #
                    json.dump(response, out_file, sort_keys=False, indent=4)
                    out_file.write('\n\n')

                # If response code is for maximum API calls per minute #
                elif response['response_code'] == 204:
                    # Print error and log #
                    print_err('Max API Error: API calls per minute maxed out at 4,'
                              ' wait 60 seconds and try again')
                    logging.exception('Max API Error: API calls per minute maxed out at 4,'
                                      ' wait 60 seconds and try again')
                    sys.exit(8)

                # If response code is for invalid request #
                elif response['response_code'] == 400:
                    # Print error and log #
                    print_err('Request Error: Invalid API request detected,'
                              ' check request formatting')
                    logging.exception('Request Error: Invalid API request detected,'
                                      ' check request formatting')
                    sys.exit(9)

                # If response code is for forbidden access #
                elif response['response_code'] == 403:
                    # Print error and log #
                    print_err('Forbidden Error: Unable to access API,'
                              ' confirm key exists and is valid')
                    logging.exception('Forbidden Error: Unable to access API,'
                                      ' confirm key exists and is valid')
                    sys.exit(10)

                # If unknown response code occurs #
                else:
                    # Print error and log #
                    print_err('Unknown response code occurred')
                    logging.exception('Unknown response code occurred')
                    sys.exit(11)

                total_count += 1
                minute_count -= 1

        # If error occurs writing to report output file #
        except OSError as file_err:
            # Lookup, display, and log IO error #
            error_query(str(report_file), 'a', file_err)

    # Store the program data for next execution #
    store_data(counter_file, total_count, execution_time_file, time_obj)


if __name__ == '__main__':
    RET = 0
    # Get the current working directory #
    cwd = Path.cwd()
    # Set the Virus Total dock for files to be scanned #
    input_dir = cwd / 'VTotalScanDock'
    # Set the log file name #
    logging.basicConfig(filename='VTotal_CLI_Log.log',
                        format='%(asctime)s %(lineno)4d@%(filename)-23s[%(levelname)s]>>  '
                               ' %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    try:
        main()

    # Ctrl + C to stop scan, store data, and exit #
    except KeyboardInterrupt:
        print('\n[!] Ctrl + c detected .. exiting program')

    # If unexpected exception occurs #
    except Exception as err:
        # Print error and log #
        print_err(f'Unexpected error occurred - {err}')
        logging.exception('Unexpected error occurred - %s', err)
        RET = 1

    sys.exit(RET)
