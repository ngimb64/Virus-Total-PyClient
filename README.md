# Virus-Total-PyClient
![alt text](https://github.com/ngimb64/Virus-Total-PyClient/blob/main/VTotalPyClient.png?raw=true)

## Prereqs
> This program runs on Windows and Linux, written in Python 3.9

## Installation
- Run the setup.py script to build a virtual environment and install all external packages in the created venv.

> Example:<br>
> python3 setup.py "venv name"

- Once virtual env is built move to the Scripts directory in the environment folder just created.
- In the Scripts directory, execute the "activate" script to activate the virtual environment.


## Purpose
> A local host client to support Virus total API calls.
> Repository contains a CLI terminal-based version, as well as a PyQt GUI version.


## How to use
- Create Virus Total account
- When logged in, get API key
- Add API key to CLI and GUI programs before executing

-- CLI --
- Open up Command Prompt (CMD) or terminal
- Enter the directory containing the program and execute in shell

-- GUI --
- Open up graphical file manager
- Find folder containing programming and double click GUI program

## Exit codes

0 - Successful execution <br>
1 - Unexpected exception occurred <br>
2 - Attempting to access file that does not exist <br>
3 - Attempting to perform operations on file that user does not have <br>
4 - IO error occurred during attempted file operation <br>
5 - Unexpected file error occurred <br>
6 - Time data in CSV file is not of integer data type <br>
7 - Error occurred querying the Virus Total API <br>
8 - If the maximum daily API call limit has been reached <br>
9 - If the request query was invalid <br>
10 - If access to the API is forbidden <br>
11 - If unknown API response code occurred <br>
