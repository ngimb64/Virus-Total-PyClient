# Built-in modules #
import hashlib
import json
import logging
import os
import sys
import time

# External modules #
import PyQt5.QtGui as Qtg
from virus_total_apis import ApiError
from virus_total_apis import PublicApi as VirusTotalPublicApi

# Custom modules #
from Modules.Utils import ErrorQuery, QtError


"""
########################################################################################################################
Name:       VTotalScan
Purpose:    Facilitates Virus Total API scans on contents of VTotalScanDock directory, sleep 60 seconds per 4 queries.
Parameters: Total Virus API key, scan directory, output report file, and the current number of daily API calls.
Returns:    The update daily number of API calls after scanning files with API.
########################################################################################################################
"""
def VTotalScan(api_key: str, scan_dir: str, out_file: str, daily_count: int, gui_outbox) -> int:
    minute_count = 4
    # Initialize the Virus-Total API object #
    vt_object = VirusTotalPublicApi(api_key)

    output_text = ''
    try:
        # Open report file in append mode #
        with open(out_file, 'a') as out_file:
            # Get the contents of input dir as list #
            for file in os.scandir(scan_dir):
                # Skip the .keep file #
                if file.name == '.keep':
                    continue

                output_text += f'{file.name}\n\n'
                # Write current file name to GUI output box #
                gui_outbox.setText(output_text)
                # Call app to update GUI output box #
                Qtg.QGuiApplication.processEvents()

                # If the maximum API calls have been used for the day #
                if daily_count == 500:
                    # write error to GUI output box #
                    gui_outbox.setText('Only 500 queries allowed per day .. exiting program')
                    # Call app to update GUI output box #
                    Qtg.QGuiApplication.processEvents()
                    break

                # If the maximum API calls have been used for the minute #
                if minute_count == 0:
                    # Write error to GUI output box #
                    gui_outbox.setText('Only 4 queries allowed per minute, sleeping 60 seconds')
                    # Call app to update GUI output box #
                    Qtg.QGuiApplication.processEvents()

                    time.sleep(60)
                    output_text = ''
                    minute_count = 4

                bytes_item = file.name.encode()

                # Generate SHA256 hash of current file in list #
                file_md5 = hashlib.sha256(bytes_item).hexdigest()
                try:
                    # Get a Virus-Total report of the hashed file #
                    response = vt_object.get_file_report(file_md5)
                # If error occurs interacting with Virus-Total API #
                except ApiError as api_err:
                    QtError(api_err)
                    logging.exception(f'API error occurred - {api_err}\n\n')
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
                    QtError('Max API Error: API calls per minute maxed out at 4,'
                            ' wait 60 seconds and try again')
                    logging.exception('Max API Error: API calls per minute maxed out at 4,'
                                      ' wait 60 seconds and try again\n\n')
                    sys.exit(8)

                # If response code is for invalid request #
                elif response['response_code'] == 400:
                    QtError('Request Error: Invalid API request detected, check request formatting')
                    logging.exception('Request Error: Invalid API request detected, check request formatting\n\n')
                    sys.exit(9)

                # If response code is for forbidden access #
                elif response['response_code'] == 403:
                    QtError('Forbidden Error: Unable to access API, confirm key exists and is valid')
                    logging.exception('Forbidden Error: Unable to access API, confirm key exists and is valid\n\n')
                    sys.exit(10)

                # If unknown response code occurs #
                else:
                    QtError('Unknown response code occurred')
                    logging.exception('Unknown response code occurred\n\n')
                    sys.exit(11)

                daily_count += 1
                minute_count -= 1

    # If error occurs writing to report output file #
    except (IOError, OSError) as err:
        QtError(err)
        # Lookup, display, and log IO error #
        ErrorQuery(out_file, 'a', err)

    return daily_count
