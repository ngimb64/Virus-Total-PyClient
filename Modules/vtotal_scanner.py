# pylint: disable=I1101
"""
Virus-Total Public API limits 500 requests per day at a rate of 4 requests per minute

Built-in modules
"""
import json
import logging
import sys
import time
# External modules #
import PyQt5.QtGui as Qtg
from virus_total_apis import PublicApi as VirusTotalPublicApi
# Custom modules #
from Modules.utils import error_query, get_files, hash_send, qt_err


def vtotal_scan(api_key: str, scan_dir: str, report_file: str, daily_count: int, gui_outbox) -> int:
    """
    Facilitates Virus Total API scans on contents of VTotalScanDock directory, sleep 60 seconds per
    4 queries.

    :param api_key:  The Virus Total API key.
    :param scan_dir:  The directory containing the files to be scanned.
    :param report_file:  The name of the output file where the report will be stored.
    :param daily_count:  The current number of daily API calls within the last recorded 24-hour
                         period
    :param gui_outbox:  Reference to Virus Total text box for updating GUI output.
    :return:  The update daily number of API calls after scanning files with API.
    """
    minute_count = 4
    # Initialize the Virus-Total API object #
    vt_object = VirusTotalPublicApi(api_key)

    # Get list of files to be scanned #
    files = get_files(scan_dir)

    output_text = ''
    try:
        # Open report file in append mode #
        with open(report_file, 'a', encoding='utf-8') as out_file:
            # Get the contents of input dir as list #
            for file in files:
                output_text += f'{file}\n\n'
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

                # Hash file and send report, return response #
                response = hash_send(file, vt_object)

                # If successful response code is returned #
                if response['response_code'] == 200:
                    # Write the name of the current file to report file #
                    out_file.write(f'File - {file}:\n{(9 + len(file)) * "*"}\n')
                    # Write json results to output report file #
                    json.dump(response, out_file, sort_keys=False, indent=4)
                    out_file.write('\n\n')

                # If response code is for maximum API calls per minute #
                elif response['response_code'] == 204:
                    # Display error on app and log #
                    qt_err('Max API Error: API calls per minute maxed out at 4,'
                           ' wait 60 seconds and try again')
                    logging.exception('Max API Error: API calls per minute maxed out at 4,'
                                      ' wait 60 seconds and try again\n\n')
                    sys.exit(8)

                # If response code is for invalid request #
                elif response['response_code'] == 400:
                    # Display error on app and log #
                    qt_err('Request Error: Invalid API request detected, check request formatting')
                    logging.exception('Request Error: Invalid API request detected,'
                                      ' check request formatting\n\n')
                    sys.exit(9)

                # If response code is for forbidden access #
                elif response['response_code'] == 403:
                    # Display error on app and log #
                    qt_err('Forbidden Error: Unable to access API,'
                            ' confirm key exists and is valid')
                    logging.exception('Forbidden Error: Unable to access API,'
                                      ' confirm key exists and is valid\n\n')
                    sys.exit(10)

                # If unknown response code occurs #
                else:
                    # Display error on app and log #
                    qt_err('Unknown response code occurred')
                    logging.exception('Unknown response code occurred\n\n')
                    sys.exit(11)

                daily_count += 1
                minute_count -= 1

    # If error occurs writing to report output file #
    except (IOError, OSError) as file_err:
        # Display error on application #
        qt_err(file_err)
        # Lookup, display, and log IO error #
        error_query(out_file, 'a', file_err)

    return daily_count
