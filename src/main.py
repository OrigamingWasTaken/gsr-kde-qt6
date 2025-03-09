#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import traceback
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

# Use relative import for local modules
# This assumes the file is in the src/ directory
from .MainWindow import GPUScreenRecorderGUI

def main():
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("GPU Screen Recorder")
        app.setOrganizationName("GPUScreenRecorder")
        app.setOrganizationDomain("github.com/gpu-screen-recorder")
        
        # Enable KDE Plasma theme integration
        app.setStyle("fusion")  # Use Fusion style which adapts better to KDE themes
        
        # Keep the app running when the window is closed
        app.setQuitOnLastWindowClosed(False)
        
        # Create and show the main window
        window = GPUScreenRecorderGUI()
        window.show()
        
        # Start the application event loop
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error starting application: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()