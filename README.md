# HMI-Data-Analysis
Analysis of Magnetogram-Related Data from the Solar Dynamics Observatory's HMI Instrument

# Files

## ProcessFiles.py
Queries HMI Instrument data through Fido API and constructs class objects from that data that represent those files.

## Magnetogram.py
Class that represents a magnetogram (solar magnetic field representation) file. Contains methods to display stats about the particular magnetogram as well as an image of what the magnetogram looks like (with and without a clip).

## AnalyzeMagnetograms.py
Uses the list of magnetogram objects constructed in ProcessFiles.py to display information to the user on any or all magnetograms.
