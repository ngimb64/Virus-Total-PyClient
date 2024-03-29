<div align="center" style="font-family: monospace">
<h1>Virus-Total-PyClient</h1>
&#9745;&#65039; Bandit verified &nbsp;|&nbsp; &#9745;&#65039; Synk verified &nbsp;|&nbsp; &#9745;&#65039; Pylint verified 9.80/10
<br>

![alt text](https://github.com/ngimb64/Virus-Total-PyClient/blob/main/VTotalPyClient.gif?raw=true)
![alt text](https://github.com/ngimb64/Virus-Total-PyClient/blob/main/VTotal_PyClient.gif?raw=true)
</div>

## Purpose
A local host client to automate Virus total API calls based on contents of scan dock folder.
The program also manages the number of API calls made within 24 hours and checks for 4 files in a row with sleep intervals to follow API rules.
Repository contains a CLI terminal-based version, as well as a PyQt GUI version.

### License
The program is licensed under [GNU Public License v3.0](LICENSE.md)

### Contributions or Issues
[CONTRIBUTING](CONTRIBUTING.md)

## Prereqs
This program runs on Windows 10 and Debian-based Linux, written in Python 3.9 and updated to version 3.10.6

## Installation
- Run the setup.py script to build a virtual environment and install all external packages in the created venv.

> Examples:<br> 
>       &emsp;&emsp;- Windows:  `python setup.py venv`<br>
>       &emsp;&emsp;- Linux:  `python3 setup.py venv`

- Once virtual env is built traverse to the (Scripts-Windows or bin-Linux) directory in the environment folder just created.
- For Windows, in the venv\Scripts directory, execute `activate` or `activate.bat` script to activate the virtual environment.
- For Linux, in the venv/bin directory, execute `source activate` to activate the virtual environment.
- If for some reason issues are experienced with the setup script, the alternative is to manually create an environment, activate it, then run pip install -r packages.txt in project root.
- To exit from the virtual environment when finished, execute `deactivate`.

## How to use
- Create Virus Total account
- When logged in, get API key
- Set VTOTAL_API_KEY environment variable with fresh API key before executing the program

> Examples:<br>
>       &emsp;&emsp;- Windows: `set VTOTAL_API_KEY=<api_key_value>`<br>
>       &emsp;&emsp;- Linux: `export VTOTAL_API_KEY=<api_key_value>`


- Confirm there is data in VTotalScanDock to be scanned

-- CLI --
- Open up Command Prompt (CMD) or terminal and activate program venv
- Enter the directory containing the program and execute in shell

-- GUI --
- Open up graphical file manager
- Find folder containing programming and double click GUI program

## Function Layout
-- cli_vtotal_pyclient.py --
> main &nbsp;-&nbsp; Gets files from input dir, iterates over them, sending and retrieving json \
> report of Virus-Total analysis of the item analyzed by the API.

-- gui_vtotal_pyclient.pyw --
> MainWindow &nbsp;-&nbsp; Class inherits the attributes of PyQT QMainWindow parent class.<br>
> &emsp; __init__ &nbsp;-&nbsp; Initialize and configure the graphical user interface.<br>
> &emsp; on_press &nbsp;-&nbsp; Executes Virus Total scanner function when button is clicked.

> main &nbsp;-&nbsp; Manages the application initialization, configuration, and exit.

-- vtotal_scanner.py --
> vtotal_scan &nbsp;-&nbsp; Facilitates Virus Total API scans on contents of VTotalScanDock \
> directory, sleep 60 seconds per 4 queries.

-- utils.py --
> counter_data_input &nbsp;-&nbsp; Reads total number of API queries from data file.

> counter_data_output &nbsp;-&nbsp; Stores total number of API queries in data file.

> error_query &nbsp;-&nbsp; Looks up the errno message to get description.

> get_files &nbsp;-&nbsp; Iterate through files in path and add to list if not the .keep file or 
> not a directory.

> hash_send &nbsp;-&nbsp Encode passed in file as bytes, perform SHA512 hash, and send hash to 
> Virus Total API. Return the result dictionary.

> load_data &nbsp;-&nbsp; Checks if exist program data exists. If so, the data loaded from the 
> files and checked to see if the 24-hour period for the 500 daily API calls is past. If it is past
> the 24-hour period the data files will be deleted to keep track of the new 24 period.

> print_err &nbsp;-&nbsp; Displays error message via standard error.

> qt_err &nbsp;-&nbsp; Prints a GUI error message with PyQT.

> store_data &nbsp;-&nbsp; Stores the API daily API counter data and execution time if first call 
> within a 24-hour period.

> time_csv_input &nbsp;-&nbsp; Reads the time data stored in csv file.

> time_csv_output &nbsp;-&nbsp; Stores execution time and data in cvs file.

> TimeTracker &nbsp;-&nbsp; Class to group the stored and current execution times.

## Exit codes
> 0 - Successful execution <br>
> 1 - Unexpected exception occurred <br>
> 2 - Attempting to access file that does not exist <br>
> 3 - Attempting to perform operations on file that user does not have <br>
> 4 - IO error occurred during attempted file operation <br>
> 5 - Unexpected file error occurred <br>
> 6 - Time data in CSV file is not of integer data type <br>
> 7 - Error occurred querying the Virus Total API <br>
> 8 - If the maximum daily API call limit has been reached <br>
> 9 - If the request query was invalid <br>
> 10 - If access to the API is forbidden <br>
> 11 - If unknown API response code occurred 
