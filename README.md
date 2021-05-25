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

[![](https://mermaid.ink/img/eyJjb2RlIjoiY2xhc3NEaWFncmFtXG4gICAgUmVzdWx0U2V0IDx8LS0gRXJyTG9nXG4gICAgUmVzdWx0U2V0IDx8LS0gU3lzbW9uXG4gICAgU3lzbW9uIDx8LS0gU2VjXG4gICAgUmVzdWx0U2V0IDogK2RhdGV0aW1lIHRpbWVfc3RhbXBcbiAgICBSZXN1bHRTZXQgOiArRGF0YUZyYW1lIGRmXG4gICAgUmVzdWx0U2V0OiArd3JpdGVfY3N2KClcbiAgICBSZXN1bHRTZXQ6ICtwbG90KClcbiAgICBjbGFzcyBFcnJMb2d7XG4gICAgICArZGljIGRpY1xuICAgICAgK2RpYyBvcHRpb25zXG4gICAgICArcHJvY2Vzc19saW5lcygpXG4gICAgfVxuICAgIGNsYXNzIFN5c21vbntcbiAgICAgICtkYXRldGltZSB0aW1lX3N0YW1wXG4gICAgICArZGljIGNvdW50ZXJcbiAgICAgICtsb2FkKClcbiAgICAgICtyZXBvcnQoKVxuICAgIH1cbiAgICBjbGFzcyBTZWN7XG4gICAgICArYWRkX3RvX2lfbGlzdCgpXG4gICAgICArZmluYWxpemUoKVxuICAgIH1cbiAgICAgICAgICAgICIsIm1lcm1haWQiOnsidGhlbWUiOiJkZWZhdWx0In0sInVwZGF0ZUVkaXRvciI6ZmFsc2V9)](https://mermaid-js.github.io/mermaid-live-editor/#/edit/eyJjb2RlIjoiY2xhc3NEaWFncmFtXG4gICAgUmVzdWx0U2V0IDx8LS0gRXJyTG9nXG4gICAgUmVzdWx0U2V0IDx8LS0gU3lzbW9uXG4gICAgU3lzbW9uIDx8LS0gU2VjXG4gICAgUmVzdWx0U2V0IDogK2RhdGV0aW1lIHRpbWVfc3RhbXBcbiAgICBSZXN1bHRTZXQgOiArRGF0YUZyYW1lIGRmXG4gICAgUmVzdWx0U2V0OiArd3JpdGVfY3N2KClcbiAgICBSZXN1bHRTZXQ6ICtwbG90KClcbiAgICBjbGFzcyBFcnJMb2d7XG4gICAgICArZGljIGRpY1xuICAgICAgK2RpYyBvcHRpb25zXG4gICAgICArcHJvY2Vzc19saW5lcygpXG4gICAgfVxuICAgIGNsYXNzIFN5c21vbntcbiAgICAgICtkYXRldGltZSB0aW1lX3N0YW1wXG4gICAgICArZGljIGNvdW50ZXJcbiAgICAgICtsb2FkKClcbiAgICAgICtyZXBvcnQoKVxuICAgIH1cbiAgICBjbGFzcyBTZWN7XG4gICAgICArYWRkX3RvX2lfbGlzdCgpXG4gICAgICArZmluYWxpemUoKVxuICAgIH1cbiAgICAgICAgICAgICIsIm1lcm1haWQiOnsidGhlbWUiOiJkZWZhdWx0In0sInVwZGF0ZUVkaXRvciI6ZmFsc2V9)


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
