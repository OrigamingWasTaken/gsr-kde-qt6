#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from pathlib import Path
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QSpinBox, QCheckBox, QGroupBox, QFileDialog, QLineEdit,
    QComboBox
)

class ReplayTab(QWidget):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Enable replay checkbox
        replay_enable_layout = QHBoxLayout()
        self.enable_replay_checkbox = QCheckBox("Enable Replay Buffer")
        self.enable_replay_checkbox.setChecked(self.settings.value("replay/enabled", False, type=bool))
        self.enable_replay_checkbox.stateChanged.connect(self.toggle_replay_options)
        
        replay_enable_layout.addWidget(self.enable_replay_checkbox)
        replay_enable_layout.addStretch()
        layout.addLayout(replay_enable_layout)
        
        # Info label
        info_layout = QHBoxLayout()
        info_label = QLabel(
            "Replay mode records continuously, but only saves the last few seconds when you press 'Save Replay'\n"
            "This is perfect for capturing moments after they happen without recording everything."
        )
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)
        layout.addLayout(info_layout)
        
        # Replay options
        self.replay_options_group = QGroupBox("Replay Options")
        self.replay_options_layout = QVBoxLayout(self.replay_options_group)
        
        # Replay buffer size
        buffer_layout = QHBoxLayout()
        self.buffer_label = QLabel("Keep Last:")
        self.buffer_spinbox = QSpinBox()
        self.buffer_spinbox.setRange(5, 1200)
        self.buffer_spinbox.setValue(int(self.settings.value("replay/buffer_size", 60)))
        self.buffer_spinbox.setSuffix(" seconds")
        
        buffer_layout.addWidget(self.buffer_label)
        buffer_layout.addWidget(self.buffer_spinbox)
        buffer_layout.addStretch()
        self.replay_options_layout.addLayout(buffer_layout)
        
        # Container format
        container_layout = QHBoxLayout()
        self.container_label = QLabel("File Format:")
        self.container_combo = QComboBox()
        
        # Use friendly names for container formats
        self.container_map = {
            "MP4 (Recommended)": "mp4",
            "MKV (More Features)": "mkv",
            "WebM (Web Compatible)": "webm"
        }
        
        self.container_combo.addItems(list(self.container_map.keys()))
        
        # Set current value from settings
        saved_container = self.settings.value("replay/container", "mp4")
        for friendly_name, value in self.container_map.items():
            if value == saved_container:
                self.container_combo.setCurrentText(friendly_name)
                break
        
        container_layout.addWidget(self.container_label)
        container_layout.addWidget(self.container_combo)
        container_layout.addStretch()
        self.replay_options_layout.addLayout(container_layout)
        
        # Restart replay on save
        restart_layout = QHBoxLayout()
        self.restart_checkbox = QCheckBox("Restart Recording After Saving Replay")
        self.restart_checkbox.setToolTip("When enabled, replays won't overlap. When disabled, saved clips may contain content from previously saved clips.")
        self.restart_checkbox.setChecked(self.settings.value("replay/restart_on_save", False, type=bool))
        
        restart_layout.addWidget(self.restart_checkbox)
        restart_layout.addStretch()
        self.replay_options_layout.addLayout(restart_layout)
        
        # Date folders
        date_folders_layout = QHBoxLayout()
        self.date_folders_checkbox = QCheckBox("Organize Replays in Date Folders")
        self.date_folders_checkbox.setChecked(self.settings.value("replay/date_folders", True, type=bool))
        
        date_folders_layout.addWidget(self.date_folders_checkbox)
        date_folders_layout.addStretch()
        self.replay_options_layout.addLayout(date_folders_layout)
        
        # Output directory
        output_dir_layout = QHBoxLayout()
        self.output_dir_label = QLabel("Save Replays To:")
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setText(self.settings.value("replay/output_dir", str(Path.home() / "Videos" / "Replays")))
        self.output_dir_btn = QPushButton("Browse")
        self.output_dir_btn.clicked.connect(self.browse_output_dir)
        
        output_dir_layout.addWidget(self.output_dir_label)
        output_dir_layout.addWidget(self.output_dir_edit)
        output_dir_layout.addWidget(self.output_dir_btn)
        self.replay_options_layout.addLayout(output_dir_layout)
        
        layout.addWidget(self.replay_options_group)
        
        # Post-processing
        self.post_processing_group = QGroupBox("After Replay Is Saved")
        self.post_processing_layout = QVBoxLayout(self.post_processing_group)
        
        # Run script checkbox
        script_enabled_layout = QHBoxLayout()
        self.script_enabled_checkbox = QCheckBox("Run Script After Saving")
        self.script_enabled_checkbox.setChecked(self.settings.value("post_processing/enabled", False, type=bool))
        self.script_enabled_checkbox.stateChanged.connect(self.toggle_script_options)
        
        script_enabled_layout.addWidget(self.script_enabled_checkbox)
        script_enabled_layout.addStretch()
        self.post_processing_layout.addLayout(script_enabled_layout)
        
        # Script path
        script_path_layout = QHBoxLayout()
        self.script_path_label = QLabel("Script Path:")
        self.script_path_edit = QLineEdit()
        self.script_path_edit.setText(self.settings.value("post_processing/script", ""))
        self.script_path_btn = QPushButton("Browse")
        self.script_path_btn.clicked.connect(self.browse_script_path)
        
        script_path_layout.addWidget(self.script_path_label)
        script_path_layout.addWidget(self.script_path_edit)
        script_path_layout.addWidget(self.script_path_btn)
        self.post_processing_layout.addLayout(script_path_layout)
        
        # Script info
        script_info_layout = QHBoxLayout()
        script_info_label = QLabel(
            "The script will be called with two arguments:\n"
            "1. Path to the saved video file\n"
            "2. Recording type ('replay')"
        )
        script_info_label.setWordWrap(True)
        script_info_layout.addWidget(script_info_label)
        self.post_processing_layout.addLayout(script_info_layout)
        
        layout.addWidget(self.post_processing_group)
        
        # Shortcuts info
        shortcuts_group = QGroupBox("Keyboard Shortcuts")
        shortcuts_layout = QVBoxLayout(shortcuts_group)
        
        shortcuts_label = QLabel(
            "Save Replay: Ctrl+Shift+S (system-wide)\n"
            "Start/Stop Recording: Ctrl+Shift+R (system-wide)\n"
            "Pause/Resume: Ctrl+Shift+P (system-wide)\n\n"
            "These shortcuts work even when the application is minimized."
        )
        shortcuts_label.setWordWrap(True)
        shortcuts_layout.addWidget(shortcuts_label)
        
        layout.addWidget(shortcuts_group)
        
        # Spacer at the bottom
        layout.addStretch()
        
        # Initial setup
        self.toggle_replay_options()
        self.toggle_script_options()
    
    def toggle_replay_options(self):
        """Enable/disable replay options based on checkbox state"""
        enabled = self.enable_replay_checkbox.isChecked()
        self.replay_options_group.setEnabled(enabled)
        self.post_processing_group.setEnabled(enabled)
    
    def toggle_script_options(self):
        """Enable/disable script options based on checkbox state"""
        enabled = self.script_enabled_checkbox.isChecked()
        self.script_path_label.setEnabled(enabled)
        self.script_path_edit.setEnabled(enabled)
        self.script_path_btn.setEnabled(enabled)
    
    def browse_output_dir(self):
        """Open file dialog to select output directory"""
        directory = QFileDialog.getExistingDirectory(
            self, 
            "Select Output Directory", 
            self.output_dir_edit.text()
        )
        if directory:
            self.output_dir_edit.setText(directory)
    
    def browse_script_path(self):
        """Open file dialog to select script file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Script File", 
            self.script_path_edit.text()
        )
        if file_path:
            self.script_path_edit.setText(file_path)
    
    def is_replay_mode(self):
        """Check if replay mode is enabled"""
        return self.enable_replay_checkbox.isChecked()
    
    def get_container_format(self):
        """Get the actual container format value from the friendly name"""
        container_text = self.container_combo.currentText()
        
        # Check if it's one of our mapped containers
        if container_text in self.container_map:
            return self.container_map[container_text]
        
        # Default to mp4 if unknown
        return "mp4"
    
    def save_settings(self):
        """Save all settings to QSettings"""
        self.settings.setValue("replay/enabled", self.enable_replay_checkbox.isChecked())
        self.settings.setValue("replay/buffer_size", self.buffer_spinbox.value())
        self.settings.setValue("replay/restart_on_save", self.restart_checkbox.isChecked())
        self.settings.setValue("replay/date_folders", self.date_folders_checkbox.isChecked())
        self.settings.setValue("replay/output_dir", self.output_dir_edit.text())
        self.settings.setValue("replay/container", self.get_container_format())
        
        # Post-processing settings
        self.settings.setValue("post_processing/enabled", self.script_enabled_checkbox.isChecked())
        self.settings.setValue("post_processing/script", self.script_path_edit.text())
    
    def build_command(self):
        """Generate command line arguments for gpu-screen-recorder in replay mode"""
        if not self.enable_replay_checkbox.isChecked():
            return []
        
        command = []
        
        # Replay buffer size
        command.extend(["-r", str(self.buffer_spinbox.value())])
        
        # Container format is required for replay mode
        container_format = self.get_container_format()
        command.extend(["-c", container_format])
        
        # Restart replay on save
        command.extend(["-restart-replay-on-save", 
                       "yes" if self.restart_checkbox.isChecked() else "no"])
        
        # Date folders
        if self.date_folders_checkbox.isChecked():
            command.extend(["-df", "yes"])
        
        # Script
        if self.script_enabled_checkbox.isChecked() and self.script_path_edit.text():
            command.extend(["-sc", self.script_path_edit.text()])
        
        # Output path
        command.extend(["-o", self.output_dir_edit.text()])
        
        return command