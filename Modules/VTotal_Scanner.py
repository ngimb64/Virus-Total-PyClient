# Built-in modules #
import hashlib
import json
import os
import sys
import time

# External modules #
from virus_total_apis import ApiError
from virus_total_apis import PublicApi as VirusTotalPublicApi

# Custom modules #
from Modules.Utils import ErrorQuery, PrintErr


"""
########################################################################################################################
Name:       VTotalScan
Purpose:    Facilitates Virus Total API scans on contents of VTotalScanDock directory, sleep 60 seconds per 4 queries.
Parameters: Total Virus API key, scan directory, output report file, and the current number of daily API calls.
Returns:    The update daily number of API calls after scanning files with API.
########################################################################################################################
"""
def VTotalScan(api_key: str, scan_dir: str, out_file: str, daily_count: int) -> int:
    minute_count = 4
    # Initialize the Virus-Total API object #
    vt_object = VirusTotalPublicApi(api_key)
    try:
        # Open report file in append mode #
        with open(out_file, 'a') as out_file:
            # Get the contents of input dir as list #
            for _, _, files in os.walk(scan_dir):
                for file in files:
                    # Skip the .keep file #
                    if file.startswith('.'):
                        continue

                    # If the maximum API calls have been used for the day #
                    if daily_count == 500:
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

                    daily_count += 1
                    minute_count -= 1

    # If error occurs writing to report output file #
    except IOError as err:
        # Lookup, display, and log IO error #
        ErrorQuery(out_file, 'a', err)

    return daily_count
