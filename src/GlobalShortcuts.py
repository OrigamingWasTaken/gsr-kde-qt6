#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from PyQt6.QtCore import QObject, QTimer
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import QApplication

class GlobalShortcutManager(QObject):
    """
    Manages global (system-wide) keyboard shortcuts using KDE's kglobalaccel
    service via D-Bus when available, with fallback to application shortcuts.
    """
    
    def __init__(self):
        super().__init__()
        self.shortcuts = {}
        self.dbus_available = False
        self.kde_available = False
        
        # Try to import dbus for KDE integration
        try:
            import dbus
            from dbus.mainloop.qt import DBusQtMainLoop
            
            # Setup D-Bus main loop
            DBusQtMainLoop(set_as_default=True)
            
            # Connect to session bus
            self.session_bus = dbus.SessionBus()
            self.dbus_available = True
            
            # Check if KDE's global accelerator service is available
            if self.session_bus.name_has_owner('org.kde.kglobalaccel'):
                self.kde_available = True
                self.kglobalaccel = self.session_bus.get_object(
                    'org.kde.kglobalaccel', 
                    '/kglobalaccel'
                )
                self.interface = dbus.Interface(
                    self.kglobalaccel, 
                    'org.kde.KGlobalAccel'
                )
                
                # Setup action monitoring for triggering callbacks
                self.setup_signal_monitoring()
                
                print("Global shortcuts using KDE's kglobalaccel service")
            else:
                print("KDE's kglobalaccel service not available, falling back to application shortcuts")
            
        except Exception as e:
            print(f"D-Bus init error: {e}, falling back to application shortcuts")
            
    def setup_signal_monitoring(self):
        """Set up monitoring for shortcut activation signals"""
        if not self.kde_available:
            return
            
        try:
            self.session_bus.add_signal_receiver(
                self._on_shortcut_triggered,
                dbus_interface='org.kde.kglobalaccel.Component',
                signal_name='globalShortcutTriggered'
            )
        except Exception as e:
            print(f"Error setting up signal monitoring: {e}")
    
    def _on_shortcut_triggered(self, shortcut_name, action_name):
        """Handler for when a shortcut is triggered"""
        shortcut_id = f"{shortcut_name}/{action_name}"
        if shortcut_id in self.shortcuts:
            # Use QTimer to ensure callback runs in the main thread
            QTimer.singleShot(0, self.shortcuts[shortcut_id])
    
    def register(self, key_sequence, callback, friendly_name=None):
        """
        Register a keyboard shortcut.
        
        Args:
            key_sequence (str): Shortcut key sequence (e.g., "Ctrl+Shift+S")
            callback (function): Function to call when shortcut is triggered
            friendly_name (str): Optional name for the shortcut
        
        Returns:
            str: Shortcut ID for later reference, or None if registration failed
        """
        if self.kde_available:
            try:
                # Generate component and action names
                app_name = "GPUScreenRecorder"
                action_name = friendly_name or f"action_{len(self.shortcuts)}"
                
                # Register with KDE's global accelerator
                self.interface.registerKey(
                    app_name,                   # Component name
                    action_name,                # Action name
                    [],                         # Default keys (empty)
                    [key_sequence],             # Active keys
                    friendly_name or "GPU Screen Recorder shortcut"
                )
                
                # Store the callback
                shortcut_id = f"{app_name}/{action_name}"
                self.shortcuts[shortcut_id] = callback
                
                return shortcut_id
                
            except Exception as e:
                print(f"Error registering global shortcut: {e}")
                # Fall back to Qt shortcut (application-only)
                return self._register_qt_shortcut(key_sequence, callback)
        else:
            # Fall back to Qt shortcut (application-only)
            return self._register_qt_shortcut(key_sequence, callback)
    
    def _register_qt_shortcut(self, key_sequence, callback):
        """Register a Qt shortcut (application-only)"""
        # Create the shortcut with application context
        if QApplication.activeWindow():
            shortcut = QShortcut(QKeySequence(key_sequence), QApplication.activeWindow())
            shortcut.activated.connect(callback)
            
            shortcut_id = f"qt_{len(self.shortcuts)}"
            self.shortcuts[shortcut_id] = callback
            return shortcut_id
        else:
            print("Warning: No active window for shortcut registration")
            return None
    
    def unregister(self, shortcut_id):
        """Unregister a specific shortcut"""
        if not shortcut_id or shortcut_id not in self.shortcuts:
            return
            
        if self.kde_available and "/" in shortcut_id:
            try:
                # Split shortcut ID
                app_name, action_name = shortcut_id.split('/')
                
                # Unregister from KGlobalAccel
                self.interface.unregisterKey(
                    app_name,
                    action_name
                )
                
                # Remove from our mapping
                del self.shortcuts[shortcut_id]
                    
            except Exception as e:
                print(f"Error unregistering global shortcut: {e}")
        
        elif shortcut_id.startswith("qt_"):
            # It's a Qt shortcut - we can't easily delete it
            # Just remove from our mapping
            del self.shortcuts[shortcut_id]
    
    def unregister_all(self):
        """Unregister all shortcuts"""
        for shortcut_id in list(self.shortcuts.keys()):
            self.unregister(shortcut_id)
        self.shortcuts = {}