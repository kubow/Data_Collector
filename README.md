# Sybase Collector

A python tkinter GUI for interacting with Sybase's (ASE, IQ and Anywhere) data. It is planned to be an universal collector for support data.


## Dependencies

- python 3+
- tkinter / Tkinter
- csv, datetime, os, sys, random, textwrap modules
- pandas (must have for managing datasets)
- (matplotlib)

## Structure

- main class MainWindow
	- btn for buttons
	- content for actual data holding
	- form for various content (stats)
	- mode_opts for mode switcher clickables
- module DbContent with classes
	- SysMon for loading 
	- ErrLog for detailed analysing timestamped logs
	- ResultSet for .txt, .csv and similar


## Implemented features

- ASE Errorlog viewer
- ASE Sysmon file viewer
- ASE Sysmon directory viewer
- ASE Resultset viewer

!!! not operational yet, for DEMO purposes

## To-Do

- Sysmon multiple mode not working
- Filtering
- dynamic loading ASA/ASE/IQ variables
