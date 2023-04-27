# Fortnite Win Probability Simulation

This Python script simulates wins and losses in Fortnite based on player statistics data retrieved from the Fortnite-API. The simulation is conducted to rank players and predict the outcome of individual match-ups between them.

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Running the Script](#running-the-script)
- [File Structure](#file-structure)
- [Technical Details](#technical-details)
- [License](#license)

## Features
- Retrieves player statistics using the Fortnite-API
- Simulates games between players based on their kill-death (KD) ratio
- Ranks players according to win percentage in simulated games
- Predicts individual match-ups between players
- Exports the overall rankings and individual match-ups to an Excel file

## Prerequisites
To use this script, you need the following:
- Python 3.8 or later
- The following Python packages: `sys`, `re`, `os`, `datetime`, `pandas`, `json`, `requests`, `numpy`, `time`, `tqdm`, and `xlsxwriter`
- A list of Fortnite player names saved in a file

## Running the Script
1. Ensure you have Python 3.8 or later installed.
2. Make sure you have all the required Python packages installed.
3. Add Fortnite player names to the `names.txt` file, with one name per line.
4. Run the script from the command line or your preferred Python environment.

## File Structure
- `main.py`: The main script that retrieves data from the Fortnite-API, simulates games, and exports the rankings and match-ups to an Excel file.
- `names.txt`: A file containing a list of Fortnite player names.

## Technical Details
- The script retrieves player statistics using the `requests` library to query the `https://fortnite-api.com/v2/stats/br/v2` endpoint.
- A DataFrame is created using `pandas` to store player data such as KD ratios.
- The simulation is based on the normal distribution, with randomness introduced using the `numpy` library.
- The `tqdm` library is utilized to display progress bars during the simulation process.
- The resulting overall rankings and individual match-ups are exported to `output_data.xlsx` file using the `xlsxwriter` library.

## License
This project is open-source and available for personal and educational use. Please credit the original author when sharing or modifying the code.
