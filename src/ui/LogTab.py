#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTextEdit, QCheckBox
)

class LogTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Log text area
        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)  # Don't wrap text
        
        # Use monospace font but don't set custom colors - let the system theme handle it
        self.log_edit.setStyleSheet("""
            QTextEdit {
                font-family: monospace;
            }
        """)
        
        layout.addWidget(self.log_edit)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Auto-scroll checkbox
        self.autoscroll_checkbox = QCheckBox("Auto-Scroll")
        self.autoscroll_checkbox.setChecked(True)
        button_layout.addWidget(self.autoscroll_checkbox)
        
        # Spacer
        button_layout.addStretch()
        
        # Clear log button
        self.clear_button = QPushButton("Clear Log")
        self.clear_button.clicked.connect(self.clear_log)
        button_layout.addWidget(self.clear_button)
        
        # Copy button
        self.copy_button = QPushButton("Copy to Clipboard")
        self.copy_button.clicked.connect(self.copy_log)
        button_layout.addWidget(self.copy_button)
        
        # Add button layout
        layout.addLayout(button_layout)
    
    def append_log(self, text):
        """Append text to log with auto-scroll"""
        self.log_edit.append(text)
        
        # Auto-scroll if enabled
        if self.autoscroll_checkbox.isChecked():
            scrollbar = self.log_edit.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
    
    def clear_log(self):
        """Clear the log"""
        self.log_edit.clear()
    
    def copy_log(self):
        """Copy log content to clipboard"""
        self.log_edit.selectAll()
        self.log_edit.copy()
        self.log_edit.moveCursor(self.log_edit.textCursor().MoveOperation.Start)  # Reset cursor