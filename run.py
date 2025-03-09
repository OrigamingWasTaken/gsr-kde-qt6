#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Launcher script for GPU Screen Recorder GUI
This script is meant to be run from the project's root directory
"""

import os
import sys

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import and run the main function
from src.main import main

if __name__ == "__main__":
    main()