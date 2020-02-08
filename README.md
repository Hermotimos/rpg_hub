# rpg_hub

## Table of contents
* [General info](#general-info)  
* [Technologies](#technologies)  
* [Setup](#setup)  
* [Features](#features)
* [Content](#content)  
* [Status](#status)  


## General info
Project started as a tutorial-based blog app, later developed as forum for a group of role playing games players. 
Site features include timeline of events, biographies of players and discussions among them, as well as an ever growing mass of knowlege (places, people, historical events) accessible to players based on the events in the real life RPG games.

## Technologies
Python 3.7 (especially pyautogui module)

## Setup
Program created and run in IDE (PyCharm 2019.1.1 Community Edition) under Windows 7.  
May be converted to .exe with pyinstaller.

## Features
Automated handling of a scraping program and browsed pages opened inside it.

## Content

### main.py
Main module.
### browsing_flow.py
Defines steps of automated browsing flow.
### report_class.py
Defines class that prints out log during execution and saves it to a report file afterwards.
### movements_and_clicks.py
Functions for reactions to site features.
### image_processing.py
Functions for recognition of site features.

## Status
TODO:  
    * Create another class for browsed pages countdown. Class would prevent resetting of browsed pages count by program recalibration in cases of RecursionError in functions.  
