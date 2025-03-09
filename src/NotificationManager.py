#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from PyQt6.QtCore import QObject, QTimer
from PyQt6.QtWidgets import QSystemTrayIcon

class NotificationManager(QObject):
    """
    Shows desktop notifications.
    Automatically chooses between Qt tray notifications and D-Bus/libnotify
    """
    
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.tray_icon = None
        self.have_dbus = False
        
        # Try to import dbus for better KDE integration
        try:
            import dbus
            self.have_dbus = True
            self.dbus = dbus
            self.session_bus = dbus.SessionBus()
            self.notification_interface = self.session_bus.get_object(
                'org.freedesktop.Notifications', 
                '/org/freedesktop/Notifications'
            )
            self.notification_service = dbus.Interface(
                self.notification_interface, 
                'org.freedesktop.Notifications'
            )
        except (ImportError, Exception) as e:
            print(f"D-Bus notification service not available: {e}", file=sys.stderr)
            self.have_dbus = False
    
    def set_tray_icon(self, tray_icon):
        """Set the tray icon to use for notifications"""
        self.tray_icon = tray_icon
    
    def notify(self, title, message, icon=None, timeout=3000):
        """
        Show a desktop notification
        
        Args:
            title (str): Notification title
            message (str): Notification message
            icon (str): Icon name or path (optional)
            timeout (int): Timeout in milliseconds
        """
        if self.have_dbus:
            # Use D-Bus for better KDE integration
            try:
                self._notify_dbus(title, message, icon, timeout)
                return
            except Exception as e:
                print(f"D-Bus notification failed: {e}", file=sys.stderr)
                # Fall through to Qt notification
        
        # Fallback to Qt tray notification
        self._notify_qt(title, message, timeout)
    
    def _notify_dbus(self, title, message, icon=None, timeout=3000):
        """Show notification using D-Bus"""
        app_name = "GPU Screen Recorder"
        replaces_id = 0  # 0 means create new notification
        icon_name = icon or "media-record"  # Use standard icon if none provided
        actions = []  # No actions
        hints = {}  # No hints
        expire_timeout = timeout  # In milliseconds
        
        self.notification_service.Notify(
            app_name, replaces_id, icon_name, title, message, 
            actions, hints, expire_timeout
        )
    
    def _notify_qt(self, title, message, timeout=3000):
        """Show notification using Qt tray icon"""
        if self.tray_icon:
            # Show notification
            self.tray_icon.showMessage(
                title, 
                message, 
                QSystemTrayIcon.MessageIcon.Information, 
                timeout
            )
        else:
            # No tray icon, print to console instead
            print(f"Notification: {title} - {message}")