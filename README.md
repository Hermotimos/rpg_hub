# rpg_hub

## Table of contents
* [General info](#general-info)  
* [Technologies](#technologies)  
* [Setup](#setup)  
* [Features](#features)
* [Content](#content)  
* [Status](#status)  


## General info
This project started as a tutorial-based blog app and developed into a forum for a group of RPG (role playing games) players. 
Site features include authorization and blog/forum like stuff; and in terms of RPG inner logic: timeline of events, biographies of players and discussions among them, as well as an ever growing mass of knowledge (places, people, historical events) accessible to players based on their participation in events unfolding in our live RPG games.

The project has been put into production as a web site, however its content is only accessible upon login due to demand for a highly customized content rendering for individual players, which corresponds to their biographies and game event participation in the live RPG game. Therefore, although it's possible for an outsider to create an account and view the site, it would be rendered to them almost entirely empty, as they wouldn't be participants of any live game events. This may seem unfortunate, but remains necessary in order to prevent unsupervised access to site content by the actual players.

While already in production the project remains a sandbox for learning new technologies. Recently: RWD, Bootstrap, JavaScript. Occasional inconsistencies and errors may result from this.

Should anybody be interested in using this code for their own RPG-like purposes or else, permission will be granted. Please contact me at lukas.kozicki@gmail.com

Note: site features have Polish names as this was created for Polish users.

Note: this project contains no docstrings due to its self-educational purpose. Modules, classes and functions are modified frequently as a result of learning process or for experiments, so keeping docstrings up-to-date would be non-ergonomic.

## Technologies
Python 3.7

Django 2.2.1

SQLite

HTML 5

CSS 3

Bootstrap 4

JavaScript 


## Setup
Requires creation of virtualenv.

Requires creation and customization of settings.py.

Requires creation of SQLite database. 

   Note: Project was created using SQLite, so some model fields and indexes may not meet standards of MySQL (particularly the sum of max_length of model fields combined within indexes).
   
Requires creation of 'media' directory with following subdirectories:
- contact_pics
- news_pics
- notes_pics
- post_pics
- profile_pics
- site_features_pics

## Features
- Authorization: creation of new accounts, login, logout, password change.
- Blog & forum: adding and responding to adverts; creating new topics; adding and responding to posts; sending and responding to individual demands; following/unfollowing news and discussions.
- Static content: rules section (contains rules for RPG game; some accessible only to specified participants).
- Customized admin (mostly inlines, filtering of querysets for M2M fields and custom forms).

## Content

Listed as per site logic, not alphabetically:
### home app
[In development] In future will contain a random selection of pictures of places and people known to the authenticated user.
### users app
User authorization, additional Profile model as an overlay for User model. Differentiates profiles into 5 categories resulting in different permissions scope (full permissions for 'game master' type of profile, restricted permissions for the rest).
### contact app
Enables sending of and responding to demands among players and game master. Also enables saving of individual plans.
### news app
Contains news and surveys for organizational purposes (next meetings, changes in rules etc.).
### rules app
Contains set of rules for the live RPG games. Some of which are accessible based on permissions granted by the 'game master' user(s).
### chronicles app
Contains timeline and chronicle sections serving as quest-logs and ongoing biographies for individual players.
### knowledge app
Contains knowledge units (packets) attributed to individual players based on their biographies and skillsets. 
### prosoponomikon app
[In development] Contains set of player & non-player characters known to individual players as per biographies and participated game events.
### toponomikon app
Contains set of places known to individual players as per biographies and participated game events.
### imaginarion app
Pictures with descriptions used by other apps.
### reload app
Quick links to re-saving of certain models whose alphabetical order depends on fields modified in overriden save() method or for firing up signals.
