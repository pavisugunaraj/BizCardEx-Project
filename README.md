# BizCardX-Extracting Business Card Data by using easyOCR (Optical Character Recognition)

## Introduction

I have developed a Streamlit application that allows users to
upload an image of a business card and extract relevant information from it using
easyOCR.

## Developer Guide

### 1. Tools Install

* Virtual code.
* Jupyter notebook.
* Python 3.11.0 or higher.
* MySQL.

### 2. Requirement Libraries to Install

* pip install pandas easyocr numpy Pillow opencv-python-headless os re sqlalchemy mysql-connector-python streamlit

### 3.Import Libraries

#### Scanning library

* import easyocr # (Optical Character Recognition)
* import numpy as np
* import matplotlib.pyplot as plt 
* import cv2
* import os
* import re

#### Data frame libraries

* import pandas as pd

#### Database Library

*import psycopg2

#### Dashboard library

* import streamlit as st

### 4. E T L Process

#### a) Extract data

* Extract relevant information from business cards by using the easyOCR library

#### b) Process and Transform the data

* After the extraction process, process the extracted data based on Company name, Card Holder, Designation, Mobile Number, Email, Website, Area, City, State, and Pincode is converted into a data frame.


