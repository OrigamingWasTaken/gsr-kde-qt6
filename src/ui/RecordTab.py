#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from pathlib import Path
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QComboBox, QSpinBox, QCheckBox, QGroupBox, QFileDialog,
    QLineEdit
)

class RecordTab(QWidget):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Capture options
        capture_group = QGroupBox("What to Record")
        capture_layout = QVBoxLayout(capture_group)
        
        # Capture source
        source_layout = QHBoxLayout()
        self.source_label = QLabel("Source:")
        self.source_combo = QComboBox()
        self.source_combo.addItems(["Screen", "Current Window", "Select Area (Portal)"])
        
        # Map friendly names to actual values
        self.source_map = {
            "Screen": "screen",
            "Current Window": "focused",
            "Select Area (Portal)": "portal"
        }
        
        # Set current value from settings
        saved_source = self.settings.value("capture/source", "portal")
        for friendly_name, value in self.source_map.items():
            if value == saved_source:
                self.source_combo.setCurrentText(friendly_name)
                break
        
        self.refresh_source_btn = QPushButton("Refresh")
        self.refresh_source_btn.clicked.connect(self.refresh_capture_sources)
        
        source_layout.addWidget(self.source_label)
        source_layout.addWidget(self.source_combo)
        source_layout.addWidget(self.refresh_source_btn)
        capture_layout.addLayout(source_layout)
        
        # Resolution
        resolution_layout = QHBoxLayout()
        self.resolution_label = QLabel("Resolution:")
        self.resolution_width = QSpinBox()
        self.resolution_width.setRange(0, 7680)
        self.resolution_width.setValue(int(self.settings.value("capture/width", 0)))
        self.resolution_height = QSpinBox()
        self.resolution_height.setRange(0, 4320)
        self.resolution_height.setValue(int(self.settings.value("capture/height", 0)))
        self.resolution_checkbox = QCheckBox("Original resolution")
        self.resolution_checkbox.setChecked(self.settings.value("capture/original_resolution", True, type=bool))
        
        resolution_layout.addWidget(self.resolution_label)
        resolution_layout.addWidget(self.resolution_width)
        resolution_layout.addWidget(QLabel("x"))
        resolution_layout.addWidget(self.resolution_height)
        resolution_layout.addWidget(self.resolution_checkbox)
        capture_layout.addLayout(resolution_layout)
        
        # FPS
        fps_layout = QHBoxLayout()
        self.fps_label = QLabel("Frame Rate:")
        self.fps_spinbox = QSpinBox()
        self.fps_spinbox.setRange(1, 240)
        self.fps_spinbox.setValue(int(self.settings.value("capture/fps", 60)))
        
        fps_layout.addWidget(self.fps_label)
        fps_layout.addWidget(self.fps_spinbox)
        fps_layout.addStretch()
        capture_layout.addLayout(fps_layout)
        
        # Show cursor
        cursor_layout = QHBoxLayout()
        self.cursor_checkbox = QCheckBox("Show Cursor")
        self.cursor_checkbox.setChecked(self.settings.value("video/show_cursor", True, type=bool))
        
        cursor_layout.addWidget(self.cursor_checkbox)
        cursor_layout.addStretch()
        capture_layout.addLayout(cursor_layout)
        
        layout.addWidget(capture_group)
        
        # Audio options
        audio_group = QGroupBox("Audio")
        audio_layout = QVBoxLayout(audio_group)
        
        # Audio sources
        audio_sources_layout = QHBoxLayout()
        self.audio_label = QLabel("Record Audio From:")
        self.audio_combo = QComboBox()
        
        # Use friendly names for common audio sources
        self.audio_map = {
            "System Sound": "default_output",
            "Microphone": "default_input",
            "System Sound + Microphone": "default_output|default_input"
        }
        
        self.audio_combo.addItems(list(self.audio_map.keys()))
        self.audio_combo.setEditable(True)
        
        # Set current value from settings
        saved_audio = self.settings.value("audio/source", "default_output")
        for friendly_name, value in self.audio_map.items():
            if value == saved_audio:
                self.audio_combo.setCurrentText(friendly_name)
                break
        else:
            self.audio_combo.setCurrentText(saved_audio)
            
        self.refresh_audio_btn = QPushButton("Refresh")
        self.refresh_audio_btn.clicked.connect(self.refresh_audio_sources)
        
        audio_sources_layout.addWidget(self.audio_label)
        audio_sources_layout.addWidget(self.audio_combo)
        audio_sources_layout.addWidget(self.refresh_audio_btn)
        audio_layout.addLayout(audio_sources_layout)
        
        layout.addWidget(audio_group)
        
        # Video quality
        video_group = QGroupBox("Video Quality")
        video_layout = QVBoxLayout(video_group)
        
        # Video quality
        quality_layout = QHBoxLayout()
        self.quality_label = QLabel("Quality:")
        self.quality_combo = QComboBox()
        
        # User-friendly names for quality levels
        self.quality_map = {
            "Low (Smaller Files)": "medium",
            "Medium": "high",
            "High (Default)": "very_high",
            "Ultra (Larger Files)": "ultra"
        }
        
        self.quality_combo.addItems(list(self.quality_map.keys()))
        
        # Set current value from settings
        saved_quality = self.settings.value("video/quality", "very_high")
        for friendly_name, value in self.quality_map.items():
            if value == saved_quality:
                self.quality_combo.setCurrentText(friendly_name)
                break
        
        quality_layout.addWidget(self.quality_label)
        quality_layout.addWidget(self.quality_combo)
        quality_layout.addStretch()
        video_layout.addLayout(quality_layout)
        
        layout.addWidget(video_group)
        
        # Output options
        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout(output_group)
        
        # Output path
        output_path_layout = QHBoxLayout()
        self.output_path_label = QLabel("Save To:")
        self.output_path_edit = QLineEdit()
        self.output_path_edit.setText(self.settings.value("output/path", str(Path.home() / "Videos")))
        self.output_path_btn = QPushButton("Browse")
        self.output_path_btn.clicked.connect(self.browse_output_path)
        
        output_path_layout.addWidget(self.output_path_label)
        output_path_layout.addWidget(self.output_path_edit)
        output_path_layout.addWidget(self.output_path_btn)
        output_layout.addLayout(output_path_layout)
        
        # Container format
        container_layout = QHBoxLayout()
        self.container_label = QLabel("Format:")
        self.container_combo = QComboBox()
        
        # Use friendly names for container formats
        self.container_map = {
            "MP4 (Recommended)": "mp4",
            "MKV (More Features)": "mkv",
            "WebM (Web Compatible)": "webm",
            "FLV (Flash Video)": "flv"
        }
        
        self.container_combo.addItems(list(self.container_map.keys()))
        
        # Set current value from settings
        saved_container = self.settings.value("output/container", "mp4")
        for friendly_name, value in self.container_map.items():
            if value == saved_container:
                self.container_combo.setCurrentText(friendly_name)
                break
        
        container_layout.addWidget(self.container_label)
        container_layout.addWidget(self.container_combo)
        container_layout.addStretch()
        output_layout.addLayout(container_layout)
        
        layout.addWidget(output_group)
        
        # Connect signals
        self.resolution_checkbox.stateChanged.connect(self.toggle_resolution)
        
        # Initial setup
        self.toggle_resolution()
    
    def toggle_resolution(self):
        enabled = not self.resolution_checkbox.isChecked()
        self.resolution_width.setEnabled(enabled)
        self.resolution_height.setEnabled(enabled)
    
    def refresh_capture_sources(self):
        import subprocess
        try:
            # Run gpu-screen-recorder --list-capture-options
            process = subprocess.Popen(
                ["gpu-screen-recorder", "--list-capture-options"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()
            
            # Process the output
            monitors = []
            for line in stdout.decode().strip().split('\n'):
                if '|' in line:
                    monitor_name = line.split('|')[0]
                    resolution = line.split('|')[1]
                    monitors.append(f"{monitor_name} ({resolution})")
            
            # Add monitors to the dropdown
            current_text = self.source_combo.currentText()
            self.source_combo.clear()
            
            # First add built-in options
            self.source_combo.addItems(["Screen", "Current Window", "Select Area (Portal)"])
            
            # Then add monitors
            if monitors:
                self.source_combo.addItems(monitors)
            
            # Try to restore previous selection
            index = self.source_combo.findText(current_text)
            if index >= 0:
                self.source_combo.setCurrentIndex(index)
        except Exception as e:
            print(f"Error refreshing capture sources: {e}")
    
    def refresh_audio_sources(self):
        import subprocess
        try:
            # Get the current selection
            current_selection = self.audio_combo.currentText()
            
            # Add standard options
            self.audio_combo.clear()
            self.audio_combo.addItems(list(self.audio_map.keys()))
            
            # Run gpu-screen-recorder --list-audio-devices
            process = subprocess.Popen(
                ["gpu-screen-recorder", "--list-audio-devices"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()
            
            # Process audio devices output
            devices = []
            for line in stdout.decode().strip().split('\n'):
                if '|' in line:
                    device_id = line.split('|')[0]
                    device_name = line.split('|')[1]
                    if device_id and device_name:
                        devices.append(f"{device_name}")
                        # Store the mapping
                        self.audio_map[device_name] = device_id
            
            # Add devices to dropdown
            if devices:
                self.audio_combo.addItems(devices)
            
            # Run gpu-screen-recorder --list-application-audio
            process = subprocess.Popen(
                ["gpu-screen-recorder", "--list-application-audio"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()
            
            # Process application audio output
            apps = []
            for line in stdout.decode().strip().split('\n'):
                app_name = line.strip()
                if app_name:
                    app_display = f"App: {app_name}"
                    apps.append(app_display)
                    # Store the mapping
                    self.audio_map[app_display] = f"app:{app_name}"
            
            # Add apps to dropdown
            if apps:
                self.audio_combo.addItems(apps)
            
            # Try to restore previous selection
            index = self.audio_combo.findText(current_selection)
            if index >= 0:
                self.audio_combo.setCurrentIndex(index)
            else:
                self.audio_combo.setCurrentText(current_selection)
        except Exception as e:
            print(f"Error refreshing audio sources: {e}")
    
    def browse_output_path(self):
        # This will be adjusted based on whether we're in replay mode
        file_filter = f"Video Files (*.{self.get_container_format()})"
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Select Output File", 
            os.path.join(self.output_path_edit.text(), f"recording.{self.get_container_format()}"),
            file_filter
        )
        if file_path:
            self.output_path_edit.setText(file_path)
    
    def save_settings(self):
        # Capture settings
        self.settings.setValue("capture/source", self.get_source())
        self.settings.setValue("capture/width", self.resolution_width.value())
        self.settings.setValue("capture/height", self.resolution_height.value())
        self.settings.setValue("capture/original_resolution", self.resolution_checkbox.isChecked())
        self.settings.setValue("capture/fps", self.fps_spinbox.value())
        
        # Audio settings
        self.settings.setValue("audio/source", self.get_audio_source())
        
        # Video settings
        self.settings.setValue("video/quality", self.get_quality())
        self.settings.setValue("video/show_cursor", self.cursor_checkbox.isChecked())
        
        # Output settings
        self.settings.setValue("output/path", self.output_path_edit.text())
        self.settings.setValue("output/container", self.get_container_format())
    
    def get_source(self):
        """Get the actual source value from the friendly name"""
        source_text = self.source_combo.currentText()
        
        # Check if it's one of our mapped sources
        if source_text in self.source_map:
            return self.source_map[source_text]
        
        # It's probably a monitor
        if "(" in source_text:
            return source_text.split(" (")[0]
        
        # Default to screen if unknown
        return "screen"
    
    def get_audio_source(self):
        """Get the actual audio source value from the friendly name"""
        audio_text = self.audio_combo.currentText()
        
        # Check if it's one of our mapped sources
        if audio_text in self.audio_map:
            return self.audio_map[audio_text]
        
        # Return as-is (might be a manually entered value)
        return audio_text
    
    def get_quality(self):
        """Get the actual quality value from the friendly name"""
        quality_text = self.quality_combo.currentText()
        
        # Check if it's one of our mapped qualities
        if quality_text in self.quality_map:
            return self.quality_map[quality_text]
        
        # Default to very_high if unknown
        return "very_high"
    
    def get_container_format(self):
        """Get the actual container format value from the friendly name"""
        container_text = self.container_combo.currentText()
        
        # Check if it's one of our mapped containers
        if container_text in self.container_map:
            return self.container_map[container_text]
        
        # Default to mp4 if unknown
        return "mp4"
    
    def build_command(self):
        """Generate command line arguments for gpu-screen-recorder"""
        command = []
        
        # Capture source
        command.extend(["-w", self.get_source()])
        
        # Resolution
        if not self.resolution_checkbox.isChecked():
            width = self.resolution_width.value()
            height = self.resolution_height.value()
            if width > 0 and height > 0:
                command.extend(["-s", f"{width}x{height}"])
        
        # FPS
        command.extend(["-f", str(self.fps_spinbox.value())])
        
        # Audio source
        audio_source = self.get_audio_source()
        if audio_source:
            command.extend(["-a", audio_source])
        
        # Show cursor
        command.extend(["-cursor", "yes" if self.cursor_checkbox.isChecked() else "no"])
        
        # Video quality
        command.extend(["-q", self.get_quality()])
        
        # Output path (this will be added by the main window)
        
        return command