#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import traceback
from pathlib import Path
from datetime import datetime

from PyQt6.QtCore import Qt, QSettings, QSize, QTimer
from PyQt6.QtGui import QAction, QIcon, QKeySequence
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QTabWidget, QStatusBar, 
    QMessageBox, QMenu, QSystemTrayIcon, QStyle
)

# Use relative imports for local modules
from .RecorderProcess import GPUScreenRecorderProcess
from .ui.RecordTab import RecordTab
from .ui.ReplayTab import ReplayTab
from .ui.AdvancedTab import AdvancedTab
from .ui.LogTab import LogTab
from .GlobalShortcuts import GlobalShortcutManager
from .NotificationManager import NotificationManager

class GPUScreenRecorderGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Set up settings
        self.settings = QSettings()
        
        # Initialize process controller
        self.recorder = GPUScreenRecorderProcess()
        self.recorder.signals.started.connect(self.on_recording_started)
        self.recorder.signals.finished.connect(self.on_recording_finished)
        self.recorder.signals.error.connect(self.show_error)
        self.recorder.signals.output.connect(self.append_log)
        
        # Recording state
        self.is_recording = False
        self.is_replay_mode = False
        self.is_paused = False
        
        # UI Setup
        self.setWindowTitle("GPU Screen Recorder")
        self.setWindowIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.setMinimumSize(700, 500)
        
        # Load window geometry and state
        self.resize(self.settings.value("window/size", QSize(800, 600)))
        self.move(self.settings.value("window/position", self.geometry().topLeft()))
        
        # Initialize UI components
        self.init_ui()
        
        # Notification manager (must be created after tray icon)
        self.notification_manager = NotificationManager()
        self.notification_manager.set_tray_icon(self.tray_icon)
        
        # Setup global shortcuts (must be done after window is created)
        self.shortcut_id_map = {}  # Store shortcut IDs for later unregistering
        self.setup_shortcuts()
        
        # Log initial debug info
        self.append_log("Application started")
        self.append_log(f"Current directory: {os.getcwd()}")
        
        # Try to find gpu-screen-recorder
        try:
            import subprocess
            result = subprocess.run(["which", "gpu-screen-recorder"], 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE, 
                                    text=True)
            if result.returncode == 0:
                self.append_log(f"Found gpu-screen-recorder at: {result.stdout.strip()}")
            else:
                self.append_log("WARNING: gpu-screen-recorder not found in PATH")
        except Exception as e:
            self.append_log(f"Error locating gpu-screen-recorder: {e}")
    
    def init_ui(self):
        # System Tray
        self.setup_tray()
        
        # Main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Tabs
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Record tab
        self.record_tab = RecordTab(self.settings)
        self.tabs.addTab(self.record_tab, "Record")
        
        # Replay tab
        self.replay_tab = ReplayTab(self.settings)
        self.tabs.addTab(self.replay_tab, "Replay")
        
        # Advanced tab
        self.advanced_tab = AdvancedTab(self.settings)
        self.tabs.addTab(self.advanced_tab, "Advanced")
        
        # Log tab
        self.log_tab = LogTab()
        self.tabs.addTab(self.log_tab, "Log")
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        # Start/Stop button
        self.start_stop_btn = QPushButton("Start Recording")
        self.start_stop_btn.clicked.connect(self.toggle_recording)
        button_layout.addWidget(self.start_stop_btn)
        
        # Save Replay button (only enabled when in replay mode)
        self.save_replay_btn = QPushButton("Save Replay")
        self.save_replay_btn.clicked.connect(self.save_replay)
        self.save_replay_btn.setEnabled(False)
        button_layout.addWidget(self.save_replay_btn)
        
        # Pause/Resume button
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.clicked.connect(self.toggle_pause)
        self.pause_btn.setEnabled(False)
        button_layout.addWidget(self.pause_btn)
        
        # Add button layout to main layout
        main_layout.addLayout(button_layout)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label, 1)
    
    def setup_tray(self):
        """Set up system tray icon with shortcut actions"""
        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.tray_icon.setToolTip("GPU Screen Recorder")
        
        # Create tray menu
        tray_menu = QMenu()
        
        # Add basic actions
        show_action = QAction("Show Window", self)
        show_action.triggered.connect(self.show)
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        
        # Add shortcut actions with key sequences in the label
        save_replay_action = QAction("Save Replay (Ctrl+Shift+S)", self)
        save_replay_action.triggered.connect(self.save_replay)
        
        toggle_record_action = QAction("Start Recording (Ctrl+Shift+R)", self)
        toggle_record_action.triggered.connect(self.toggle_recording)
        
        toggle_pause_action = QAction("Pause/Resume (Ctrl+Shift+P)", self)
        toggle_pause_action.triggered.connect(self.toggle_pause)
        
        # Create a shortcuts sub-menu
        shortcuts_menu = QMenu("Shortcuts")
        shortcuts_menu.addAction(save_replay_action)
        shortcuts_menu.addAction(toggle_record_action)
        shortcuts_menu.addAction(toggle_pause_action)
        
        # Populate menu
        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        tray_menu.addMenu(shortcuts_menu)  # Add shortcuts as a submenu
        tray_menu.addSeparator()
        tray_menu.addAction(toggle_record_action)  # Also keep the main toggle action in the root menu
        tray_menu.addAction(save_replay_action)    # And the save replay action
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        
        # Set context menu
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # Connect tray icon activation
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
        # Store references for later updates
        self.toggle_record_action = toggle_record_action
        self.save_replay_action = save_replay_action
        self.toggle_pause_action = toggle_pause_action

    def tray_icon_activated(self, reason):
        """Handle tray icon activation (click, double-click)"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Single click - show menu
            pass
        elif reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            # Double click - toggle recording
            self.toggle_recording()
        elif reason == QSystemTrayIcon.ActivationReason.MiddleClick:
            # Middle click - save replay
            self.save_replay()
        
    def setup_shortcuts(self):
        """Set up application keyboard shortcuts"""
        from PyQt6.QtGui import QShortcut, QKeySequence
        
        # Create shortcut for save replay (Ctrl+Shift+S)
        save_shortcut = QShortcut(QKeySequence("Ctrl+Shift+S"), self)
        save_shortcut.activated.connect(self.save_replay)
        
        # Create shortcut for toggle recording (Ctrl+Shift+R)
        record_shortcut = QShortcut(QKeySequence("Ctrl+Shift+R"), self)
        record_shortcut.activated.connect(self.toggle_recording)
        
        # Create shortcut for pause/resume (Ctrl+Shift+P)
        pause_shortcut = QShortcut(QKeySequence("Ctrl+Shift+P"), self)
        pause_shortcut.activated.connect(self.toggle_pause)
        
        # Store references for later
        self.shortcuts = [save_shortcut, record_shortcut, pause_shortcut]
        
        # Log the shortcuts
        self.append_log("Keyboard shortcuts registered: Ctrl+Shift+S (Save), Ctrl+Shift+R (Record), Ctrl+Shift+P (Pause)")

        
    def build_command(self):
        command = ["gpu-screen-recorder"]
        
        # Get values from UI tabs
        try:
            # Record tab
            record_cmd = self.record_tab.build_command()
            self.append_log(f"Record tab command: {record_cmd}")
            command.extend(record_cmd)
            
            # Replay mode
            if self.is_replay_mode:
                replay_cmd = self.replay_tab.build_command()
                self.append_log(f"Replay tab command: {replay_cmd}")
                command.extend(replay_cmd)
            
            # Advanced tab
            advanced_cmd = self.advanced_tab.build_command()
            self.append_log(f"Advanced tab command: {advanced_cmd}")
            command.extend(advanced_cmd)
            
            # Final validation
            if "-o" not in command:
                raise ValueError("No output path specified")
                
            return command
            
        except Exception as e:
            self.show_error(f"Error building command: {str(e)}")
            self.append_log(f"Error stack: {traceback.format_exc()}")
            # Return a safe default command if error occurs
            return ["gpu-screen-recorder", "--help"]
    
    def toggle_recording(self):
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()
    
    def start_recording(self):
        try:
            # Determine if this is replay mode or regular recording
            self.is_replay_mode = self.replay_tab.is_replay_mode()
            self.append_log(f"Replay mode: {self.is_replay_mode}")
            
            # Build command
            command = self.build_command()
            
            # Log command
            self.append_log(f"Starting: {' '.join(command)}")
            
            # Start the process
            self.recorder.start(command)
            
            # Update UI
            self.is_recording = True
            self.is_paused = False
            self.start_stop_btn.setText("Stop Recording")
            self.pause_btn.setEnabled(True)
            self.pause_btn.setText("Pause")
            self.save_replay_btn.setEnabled(self.is_replay_mode)
            self.toggle_record_action.setText("Stop Recording")
            
            # Update status
            if self.is_replay_mode:
                self.status_label.setText("Replay buffer active")
                # Show notification
                self.notification_manager.notify("GPU Screen Recorder", "Replay buffer started")
            else:
                self.status_label.setText("Recording")
                # Show notification
                self.notification_manager.notify("GPU Screen Recorder", "Recording started")
            
            # Save settings
            self.save_settings()
            
        except Exception as e:
            import traceback
            self.show_error(f"Error starting recording: {str(e)}")
            self.append_log(f"Error stack: {traceback.format_exc()}")
    
    def stop_recording(self):
        # Stop the process
        self.recorder.stop()
        
        # Update UI
        self.is_recording = False
        self.is_paused = False
        self.start_stop_btn.setText("Start Recording")
        self.pause_btn.setEnabled(False)
        self.pause_btn.setText("Pause")
        self.save_replay_btn.setEnabled(False)
        self.toggle_record_action.setText("Start Recording")
        
        # Update status
        self.status_label.setText("Ready")
        
        # Show notification
        if self.is_replay_mode:
            self.notification_manager.notify("GPU Screen Recorder", "Replay buffer stopped")
        else:
            self.notification_manager.notify("GPU Screen Recorder", "Recording stopped")
    
    def toggle_pause(self):
        if not self.is_recording:
            return
        
        if self.recorder.toggle_pause():
            self.is_paused = not self.is_paused
            if self.is_paused:
                self.pause_btn.setText("Resume")
                self.status_label.setText("Paused")
                # Show notification
                self.notification_manager.notify("GPU Screen Recorder", "Recording paused")
            else:
                self.pause_btn.setText("Pause")
                self.status_label.setText("Recording" if not self.is_replay_mode else "Replay buffer active")
                # Show notification
                self.notification_manager.notify("GPU Screen Recorder", "Recording resumed")
    
    def save_replay(self):
        if not self.is_recording or not self.is_replay_mode:
            QMessageBox.warning(self, "Not in Replay Mode", "You need to start replay buffer first.")
            return
        
        if self.recorder.save_replay():
            self.append_log("Replay saved")
            self.status_label.setText("Replay saved")
            
            # Show notification
            self.notification_manager.notify("GPU Screen Recorder", "Replay saved", timeout=5000)
            
            # Reset after 2 seconds
            QTimer.singleShot(2000, lambda: self.status_label.setText("Replay buffer active" if self.is_recording else "Ready"))
    
    def on_recording_started(self):
        self.append_log("Recording started")
    
    def on_recording_finished(self):
        if self.is_recording:
            self.is_recording = False
            self.start_stop_btn.setText("Start Recording")
            self.pause_btn.setEnabled(False)
            self.save_replay_btn.setEnabled(False)
            self.toggle_record_action.setText("Start Recording")
            self.status_label.setText("Ready")
            self.append_log("Recording finished")
    
    def append_log(self, text):
        current_time = datetime.now().strftime("%H:%M:%S")
        if hasattr(self, 'log_tab'):
            self.log_tab.append_log(f"[{current_time}] {text}")
        else:
            print(f"[{current_time}] {text}")
    
    def show_error(self, error_msg):
        self.append_log(f"ERROR: {error_msg}")
        QMessageBox.critical(self, "Error", error_msg)
    
    def save_settings(self):
        # Save window geometry
        self.settings.setValue("window/size", self.size())
        self.settings.setValue("window/position", self.pos())
        
        # Save tab settings
        self.record_tab.save_settings()
        self.replay_tab.save_settings()
        self.advanced_tab.save_settings()
    
    def closeEvent(self, event):
        # Save settings
        self.save_settings()
        
        # Stop recording if active
        if self.is_recording:
            self.stop_recording()
        
        # Unregister global shortcuts
        if hasattr(self, 'shortcut_manager'):
            self.shortcut_manager.unregister_all()
        
        # Accept the close event
        event.accept()