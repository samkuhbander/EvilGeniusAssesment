# EvilGeniusAssesment

This README contains the description of a Python class ProcessGameState developed for analyzing the gaming stats. It also includes the method definitions and some sample results.

## Overview
This program is designed to analyze game states in a match. It can process weapon classes, area names, team strategies, and even the average time to reach certain areas.

## Installation

Clone the repository
pip install -r requirements.txt


## Class Description: ProcessGameState
This class is designed to handle game data processing tasks.

#### Methods
load_data(): Load the parquet file and store it in a DataFrame.

clean_data(): Remove null values from the DataFrame.

check_boundaries(): Check whether each row falls within a provided boundary.

extract_weapon_classes(): Extract weapon classes from the inventory column.

extract_area_names(): Extract area names from the area_name column.

player_has_rifle_or_smg(): Check if the player's inventory contains a rifle or SMG.

process(): Load, clean, and check boundaries in the data. Extract weapon classes and area names and print them out.

average_entry_time(): Calculate the average time that a team enters a specific area with a minimum number of weapons.

plot_heatmap_on_map(): Plot a heatmap of player positions on a given map.

entry_frequency(): Calculate the frequency of a team entering a boundary.

## Usage
The class ProcessGameState can be used to analyze the game data and we obtained the following results:

We found four weapon classes: ['Rifle', 'Grenade', 'Pistols', 'SMG']
We found twenty-five area names.
We observed that the frequency of Team2 entering the light blue boundary on T side is approximately 6.67%.
The average timer for Team2 entering the light blue boundary on T side was found to be 01:07.
The class also includes a method to generate a heatmap to examine Team2's positioning on the CT side within "BombsiteB".
The heatmap is saved as Team2CTBombsiteB.png

A solution for the product manager:
Develop a lightweight web application using frameworks such as Flask or Django for the backend (which runs Python), and a simple frontend using HTML/CSS/Javascript.

The web application will have forms where the coaching staff can input their requirements (e.g., team names, areas, weapon classes, etc.). Upon form submission, the data will be sent to the backend, where the Python code will run and generate the requested data or insights. The results can then be displayed in the browser in a user-friendly format (tables, graphs, etc.). This can be done in a week if the complexity of the UI is kept minimal and the focus is on functionality.

## Requirements
Python 3.6+
Packages: pandas, os, matplotlib, numpy, seaborn, functools
