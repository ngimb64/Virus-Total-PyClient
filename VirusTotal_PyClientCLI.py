""" The Virus-Total Public API is limited to 500 requests per day and a rate of 4 requests per minute """

# Built-in modules #
import hashlib
import json
import logging
import os
import sys
import time
from datetime import datetime

# External modules #
from virus_total_apis import ApiError
from virus_total_apis import PublicApi as VirusTotalPublicApi

# Custom modules #
from Modules.Utils import ErrorQuery, LoadProgramData, PrintErr, StoreProgramData


# Pseudo constants #
API_KEY = '< Add API key here >'
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
    # Get the current execution time #
    start_time = datetime.now()
    month, day, hour = start_time.month, start_time.day, start_time.hour

    report_file = f'VirusTotalReport_{month}-{day}-{hour}.txt'
    counter_file = 'counter_data.data'
    execution_time_file = 'last_execution_time.csv'

    # Load the program data (API daily call count & exec time of first call) #
    total_count, old_month, old_day, old_hour = LoadProgramData(counter_file, execution_time_file, month, day, hour)

    # Initialize the Virus-Total API object #
    vt_object = VirusTotalPublicApi(API_KEY)
    minute_count = 4

    print(f'Current number of daily Virus-Total API queries: {total_count}\n')
    print(f'Starting Virus-Total file check on file in {INPUT_DIR}')
    print(f'{(44 + len(INPUT_DIR)) * "*"}')
    try:
        # Open report file in append mode #
        with open(report_file, 'a') as out_file:
            # Get the contents of input dir as list #
            for file in os.scandir(INPUT_DIR):
                # Skip the .keep file #
                if file.name == '.keep':
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

                print(f'Generating report for: {file.name}')
                bytes_item = file.name.encode()

                # Generate SHA256 hash of current file in list #
                file_md5 = hashlib.sha256(bytes_item).hexdigest()
                try:
                    # Get a Virus-Total report of the hashed file #
                    response = vt_object.get_file_report(file_md5)
                # If error occurs interacting with Virus-Total API #
                except ApiError as api_err:
                    PrintErr(f'API error occurred - {api_err}')
                    sys.exit(7)

                # If successful response code is returned #
                if response['response_code'] == 200:
                    # Write the name of the current file to report file #
                    out_file.write(f'File - {file.name}:\n{(9 + len(file.name)) * "*"}\n')
                    # Write json results to output report file #
                    json.dump(response, out_file, sort_keys=False, indent=4)
                    out_file.write('\n\n')

                # If response code is for maximum API calls per minute #
                elif response['response_code'] == 204:
                    PrintErr('Max API Error: API calls per minute maxed out at 4, wait 60 seconds and try again')
                    sys.exit(8)

                # If response code is for invalid request #
                elif response['response_code'] == 400:
                    PrintErr('Request Error: Invalid API request detected, check request formatting')
                    sys.exit(9)

                # If response code is for forbidden access #
                elif response['response_code'] == 403:
                    PrintErr('Forbidden Error: Unable to access API, confirm key exists and is valid')
                    sys.exit(10)

                # If unknown response code occurs #
                else:
                    PrintErr('Unknown response code occurred')
                    sys.exit(11)

                total_count += 1
                minute_count -= 1

    # Ctrl + C to stop scan, store data, and exit #
    except KeyboardInterrupt:
        pass

    # If error occurs writing to report output file #
    except (IOError, OSError) as file_err:
        ErrorQuery(report_file, 'a', file_err)

    # Store the program data for next execution #
    StoreProgramData(counter_file, total_count, execution_time_file, old_month, old_day, old_hour, day, hour)


if __name__ == '__main__':
    # Initialize logging facilities #
    logging.basicConfig(level=logging.DEBUG, filename='VTotal_CliLog.log')

    try:
        main()

    # If unexpected exception occurs #
    except Exception as err:
        PrintErr(f'Unexpected error occurred - {err}')
        logging.exception(f'Unexpected error occurred - {err}\n\n')
        sys.exit(1)

    sys.exit(0)
