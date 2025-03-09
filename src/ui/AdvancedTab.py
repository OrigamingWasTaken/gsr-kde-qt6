#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QDoubleSpinBox, QCheckBox, QGroupBox, 
    QTabWidget, QSpinBox
)

class AdvancedTab(QWidget):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Warning label at the top
        warning_layout = QHBoxLayout()
        warning_label = QLabel(
            "⚠️ These settings are for advanced users. The default values work well for most cases."
        )
        warning_label.setStyleSheet("color: #FF8C00;")  # Orange warning color
        warning_layout.addWidget(warning_label)
        layout.addLayout(warning_layout)
        
        # Create inner tabs for better organization of advanced settings
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Video tab
        video_tab = QWidget()
        video_layout = QVBoxLayout(video_tab)
        
        # Video codec options
        codec_group = QGroupBox("Video Codec Options")
        codec_layout = QVBoxLayout(codec_group)
        
        # Video codec
        codec_select_layout = QHBoxLayout()
        self.codec_label = QLabel("Codec:")
        self.codec_combo = QComboBox()
        
        # Use friendly names for codecs
        self.codec_map = {
            "Auto (Recommended)": "auto",
            "H.264 (Good Compatibility)": "h264",
            "HEVC/H.265 (Better Compression)": "hevc",
            "AV1 (Best Compression, New)": "av1",
            "VP8 (WebM)": "vp8",
            "VP9 (WebM, Better)": "vp9",
            "HEVC HDR": "hevc_hdr",
            "AV1 HDR": "av1_hdr",
            "HEVC 10-bit": "hevc_10bit",
            "AV1 10-bit": "av1_10bit"
        }
        
        self.codec_combo.addItems(list(self.codec_map.keys()))
        
        # Set current value from settings
        saved_codec = self.settings.value("video/codec", "auto")
        for friendly_name, value in self.codec_map.items():
            if value == saved_codec:
                self.codec_combo.setCurrentText(friendly_name)
                break
        
        codec_select_layout.addWidget(self.codec_label)
        codec_select_layout.addWidget(self.codec_combo)
        codec_select_layout.addStretch()
        codec_layout.addLayout(codec_select_layout)
        
        # Bitrate mode
        bitrate_mode_layout = QHBoxLayout()
        self.bitrate_mode_label = QLabel("Bitrate Mode:")
        self.bitrate_mode_combo = QComboBox()
        
        # Use friendly names for bitrate modes
        self.bitrate_mode_map = {
            "Auto (Recommended)": "auto",
            "Constant Quality (Varies Size)": "qp",
            "Variable Bitrate (Balanced)": "vbr",
            "Constant Bitrate (Fixed Size)": "cbr"
        }
        
        self.bitrate_mode_combo.addItems(list(self.bitrate_mode_map.keys()))
        self.bitrate_mode_combo.currentTextChanged.connect(self.update_bitrate_controls)
        
        # Set current value from settings
        saved_mode = self.settings.value("video/bitrate_mode", "auto")
        for friendly_name, value in self.bitrate_mode_map.items():
            if value == saved_mode:
                self.bitrate_mode_combo.setCurrentText(friendly_name)
                break
        
        bitrate_mode_layout.addWidget(self.bitrate_mode_label)
        bitrate_mode_layout.addWidget(self.bitrate_mode_combo)
        bitrate_mode_layout.addStretch()
        codec_layout.addLayout(bitrate_mode_layout)
        
        # CBR bitrate (only visible in CBR mode)
        self.cbr_layout = QHBoxLayout()
        self.cbr_label = QLabel("Target Bitrate:")
        self.cbr_spinbox = QSpinBox()
        self.cbr_spinbox.setRange(1000, 100000)
        self.cbr_spinbox.setValue(int(self.settings.value("video/cbr_bitrate", 15000)))
        self.cbr_spinbox.setSuffix(" kbps")
        
        self.cbr_layout.addWidget(self.cbr_label)
        self.cbr_layout.addWidget(self.cbr_spinbox)
        self.cbr_layout.addStretch()
        codec_layout.addLayout(self.cbr_layout)
        
        # Color range
        color_range_layout = QHBoxLayout()
        self.color_range_label = QLabel("Color Range:")
        self.color_range_combo = QComboBox()
        
        # Use friendly names for color ranges
        self.color_range_map = {
            "Limited (Standard/Rec.709)": "limited",
            "Full (Enhanced/High Quality)": "full"
        }
        
        self.color_range_combo.addItems(list(self.color_range_map.keys()))
        
        # Set current value from settings
        saved_range = self.settings.value("video/color_range", "limited")
        for friendly_name, value in self.color_range_map.items():
            if value == saved_range:
                self.color_range_combo.setCurrentText(friendly_name)
                break
        
        color_range_layout.addWidget(self.color_range_label)
        color_range_layout.addWidget(self.color_range_combo)
        color_range_layout.addStretch()
        codec_layout.addLayout(color_range_layout)
        
        # Frame rate mode
        frame_mode_layout = QHBoxLayout()
        self.frame_mode_label = QLabel("Frame Rate Mode:")
        self.frame_mode_combo = QComboBox()
        
        # Use friendly names for frame rate modes
        self.frame_mode_map = {
            "Variable (Recommended)": "vfr",
            "Constant (Consistent)": "cfr",
            "Match Content (Smart)": "content"
        }
        
        self.frame_mode_combo.addItems(list(self.frame_mode_map.keys()))
        
        # Set current value from settings
        saved_frame_mode = self.settings.value("capture/frame_mode", "vfr")
        for friendly_name, value in self.frame_mode_map.items():
            if value == saved_frame_mode:
                self.frame_mode_combo.setCurrentText(friendly_name)
                break
        
        frame_mode_layout.addWidget(self.frame_mode_label)
        frame_mode_layout.addWidget(self.frame_mode_combo)
        frame_mode_layout.addStretch()
        codec_layout.addLayout(frame_mode_layout)
        
        # Keyframe interval
        keyframe_layout = QHBoxLayout()
        self.keyframe_label = QLabel("Keyframe Interval:")
        self.keyframe_spinbox = QDoubleSpinBox()
        self.keyframe_spinbox.setRange(0.1, 10.0)
        self.keyframe_spinbox.setSingleStep(0.1)
        self.keyframe_spinbox.setValue(float(self.settings.value("advanced/keyframe_interval", 2.0)))
        self.keyframe_spinbox.setSuffix(" seconds")
        
        keyframe_layout.addWidget(self.keyframe_label)
        keyframe_layout.addWidget(self.keyframe_spinbox)
        keyframe_layout.addStretch()
        codec_layout.addLayout(keyframe_layout)
        
        video_layout.addWidget(codec_group)
        
        # Encoder options
        encoder_group = QGroupBox("Hardware Acceleration")
        encoder_layout = QVBoxLayout(encoder_group)
        
        # Encoder selection
        encoder_select_layout = QHBoxLayout()
        self.encoder_label = QLabel("Encoder:")
        self.encoder_combo = QComboBox()
        
        # Use friendly names for encoders
        self.encoder_map = {
            "GPU (Recommended)": "gpu",
            "CPU (Software Encoding)": "cpu"
        }
        
        self.encoder_combo.addItems(list(self.encoder_map.keys()))
        
        # Set current value from settings
        saved_encoder = self.settings.value("advanced/encoder", "gpu")
        for friendly_name, value in self.encoder_map.items():
            if value == saved_encoder:
                self.encoder_combo.setCurrentText(friendly_name)
                break
        
        encoder_select_layout.addWidget(self.encoder_label)
        encoder_select_layout.addWidget(self.encoder_combo)
        encoder_select_layout.addStretch()
        encoder_layout.addLayout(encoder_select_layout)
        
        # NVIDIA overclock
        overclock_layout = QHBoxLayout()
        self.overclock_checkbox = QCheckBox("Overclock Memory Transfer Rate (NVIDIA only)")
        self.overclock_checkbox.setToolTip("Helps if recording performance drops in games. Requires Coolbits=12 in your NVIDIA X settings")
        self.overclock_checkbox.setChecked(self.settings.value("advanced/overclock", False, type=bool))
        
        overclock_layout.addWidget(self.overclock_checkbox)
        overclock_layout.addStretch()
        encoder_layout.addLayout(overclock_layout)
        
        video_layout.addWidget(encoder_group)
        video_layout.addStretch()
        
        # Audio tab
        audio_tab = QWidget()
        audio_layout = QVBoxLayout(audio_tab)
        
        # Audio codec options
        audio_codec_group = QGroupBox("Audio Codec Options")
        audio_codec_layout = QVBoxLayout(audio_codec_group)
        
        # Audio codec
        audio_codec_select_layout = QHBoxLayout()
        self.audio_codec_label = QLabel("Audio Codec:")
        self.audio_codec_combo = QComboBox()
        
        # Use friendly names for audio codecs
        self.audio_codec_map = {
            "Opus (Better Quality)": "opus",
            "AAC (Better Compatibility)": "aac"
        }
        
        self.audio_codec_combo.addItems(list(self.audio_codec_map.keys()))
        
        # Set current value from settings
        saved_audio_codec = self.settings.value("audio/codec", "opus")
        for friendly_name, value in self.audio_codec_map.items():
            if value == saved_audio_codec:
                self.audio_codec_combo.setCurrentText(friendly_name)
                break
        
        audio_codec_select_layout.addWidget(self.audio_codec_label)
        audio_codec_select_layout.addWidget(self.audio_codec_combo)
        audio_codec_select_layout.addStretch()
        audio_codec_layout.addLayout(audio_codec_select_layout)
        
        # Audio bitrate
        audio_bitrate_layout = QHBoxLayout()
        self.audio_bitrate_label = QLabel("Audio Bitrate:")
        self.audio_bitrate_spinbox = QSpinBox()
        self.audio_bitrate_spinbox.setRange(0, 500)
        self.audio_bitrate_spinbox.setValue(int(self.settings.value("audio/bitrate", 128)))
        self.audio_bitrate_spinbox.setSuffix(" kbps")
        self.audio_bitrate_checkbox = QCheckBox("Automatic")
        self.audio_bitrate_checkbox.setChecked(self.settings.value("audio/auto_bitrate", True, type=bool))
        self.audio_bitrate_checkbox.stateChanged.connect(self.toggle_audio_bitrate)
        
        audio_bitrate_layout.addWidget(self.audio_bitrate_label)
        audio_bitrate_layout.addWidget(self.audio_bitrate_spinbox)
        audio_bitrate_layout.addWidget(self.audio_bitrate_checkbox)
        audio_bitrate_layout.addStretch()
        audio_codec_layout.addLayout(audio_bitrate_layout)
        
        audio_layout.addWidget(audio_codec_group)
        audio_layout.addStretch()
        
        # Misc tab
        misc_tab = QWidget()
        misc_layout = QVBoxLayout(misc_tab)
        
        # Wayland options
        wayland_group = QGroupBox("Wayland Options")
        wayland_layout = QVBoxLayout(wayland_group)
        
        # Portal session
        portal_session_layout = QHBoxLayout()
        self.portal_session_checkbox = QCheckBox("Restore Portal Session")
        self.portal_session_checkbox.setToolTip("Remember screen selection in Wayland portal. Only works with desktop portal version 5+")
        self.portal_session_checkbox.setChecked(self.settings.value("advanced/restore_portal_session", False, type=bool))
        
        portal_session_layout.addWidget(self.portal_session_checkbox)
        portal_session_layout.addStretch()
        wayland_layout.addLayout(portal_session_layout)
        
        misc_layout.addWidget(wayland_group)
        
        # Debug options
        debug_group = QGroupBox("Debug Options")
        debug_layout = QVBoxLayout(debug_group)
        
        # Verbose output
        verbose_layout = QHBoxLayout()
        self.verbose_checkbox = QCheckBox("Enable Verbose Output")
        self.verbose_checkbox.setToolTip("Print detailed information during recording")
        self.verbose_checkbox.setChecked(self.settings.value("advanced/verbose", True, type=bool))
        
        verbose_layout.addWidget(self.verbose_checkbox)
        verbose_layout.addStretch()
        debug_layout.addLayout(verbose_layout)
        
        misc_layout.addWidget(debug_group)
        misc_layout.addStretch()
        
        # Add tabs to the tabwidget
        tabs.addTab(video_tab, "Video")
        tabs.addTab(audio_tab, "Audio")
        tabs.addTab(misc_tab, "Misc")
        
        # Initial setup
        self.update_bitrate_controls()
        self.toggle_audio_bitrate()
    
    def update_bitrate_controls(self):
        """Enable/disable and adjust bitrate controls based on selected mode"""
        # Get current bitrate mode
        selected_mode = self.get_bitrate_mode()
        
        # Show/hide CBR controls
        is_cbr = selected_mode == "cbr"
        self.cbr_label.setEnabled(is_cbr)
        self.cbr_spinbox.setEnabled(is_cbr)
    
    def toggle_audio_bitrate(self):
        """Enable/disable audio bitrate spinbox based on checkbox state"""
        enabled = not self.audio_bitrate_checkbox.isChecked()
        self.audio_bitrate_spinbox.setEnabled(enabled)
    
    def get_codec(self):
        """Get the actual codec value from the friendly name"""
        codec_text = self.codec_combo.currentText()
        
        # Check if it's one of our mapped codecs
        if codec_text in self.codec_map:
            return self.codec_map[codec_text]
        
        # Default to auto if unknown
        return "auto"
    
    def get_bitrate_mode(self):
        """Get the actual bitrate mode value from the friendly name"""
        mode_text = self.bitrate_mode_combo.currentText()
        
        # Check if it's one of our mapped modes
        if mode_text in self.bitrate_mode_map:
            return self.bitrate_mode_map[mode_text]
        
        # Default to auto if unknown
        return "auto"
    
    def get_color_range(self):
        """Get the actual color range value from the friendly name"""
        range_text = self.color_range_combo.currentText()
        
        # Check if it's one of our mapped ranges
        if range_text in self.color_range_map:
            return self.color_range_map[range_text]
        
        # Default to limited if unknown
        return "limited"
    
    def get_frame_mode(self):
        """Get the actual frame mode value from the friendly name"""
        mode_text = self.frame_mode_combo.currentText()
        
        # Check if it's one of our mapped modes
        if mode_text in self.frame_mode_map:
            return self.frame_mode_map[mode_text]
        
        # Default to vfr if unknown
        return "vfr"
    
    def get_encoder(self):
        """Get the actual encoder value from the friendly name"""
        encoder_text = self.encoder_combo.currentText()
        
        # Check if it's one of our mapped encoders
        if encoder_text in self.encoder_map:
            return self.encoder_map[encoder_text]
        
        # Default to gpu if unknown
        return "gpu"
    
    def get_audio_codec(self):
        """Get the actual audio codec value from the friendly name"""
        codec_text = self.audio_codec_combo.currentText()
        
        # Check if it's one of our mapped codecs
        if codec_text in self.audio_codec_map:
            return self.audio_codec_map[codec_text]
        
        # Default to opus if unknown
        return "opus"
    
    def save_settings(self):
        """Save all settings to QSettings"""
        # Video settings
        self.settings.setValue("video/codec", self.get_codec())
        self.settings.setValue("video/bitrate_mode", self.get_bitrate_mode())
        self.settings.setValue("video/cbr_bitrate", self.cbr_spinbox.value())
        self.settings.setValue("video/color_range", self.get_color_range())
        
        # Capture settings
        self.settings.setValue("capture/frame_mode", self.get_frame_mode())
        
        # Audio settings
        self.settings.setValue("audio/codec", self.get_audio_codec())
        self.settings.setValue("audio/bitrate", self.audio_bitrate_spinbox.value())
        self.settings.setValue("audio/auto_bitrate", self.audio_bitrate_checkbox.isChecked())
        
        # Advanced settings
        self.settings.setValue("advanced/encoder", self.get_encoder())
        self.settings.setValue("advanced/keyframe_interval", self.keyframe_spinbox.value())
        self.settings.setValue("advanced/restore_portal_session", self.portal_session_checkbox.isChecked())
        self.settings.setValue("advanced/overclock", self.overclock_checkbox.isChecked())
        self.settings.setValue("advanced/verbose", self.verbose_checkbox.isChecked())
    
    def build_command(self):
        """Generate command line arguments for gpu-screen-recorder advanced options"""
        command = []
        
        # Video codec
        command.extend(["-k", self.get_codec()])
        
        # Frame rate mode
        command.extend(["-fm", self.get_frame_mode()])
        
        # Audio codec
        command.extend(["-ac", self.get_audio_codec()])
        
        # Audio bitrate
        if not self.audio_bitrate_checkbox.isChecked():
            command.extend(["-ab", str(self.audio_bitrate_spinbox.value())])
        
        # Bitrate mode
        command.extend(["-bm", self.get_bitrate_mode()])
        
        # CBR bitrate
        if self.get_bitrate_mode() == "cbr":
            command.extend(["-q", str(self.cbr_spinbox.value())])
        
        # Color range
        command.extend(["-cr", self.get_color_range()])
        
        # Keyframe interval
        command.extend(["-keyint", str(self.keyframe_spinbox.value())])
        
        # Encoder
        command.extend(["-encoder", self.get_encoder()])
        
        # Overclock
        if self.overclock_checkbox.isChecked():
            command.extend(["-oc", "yes"])
        
        # Portal session
        if self.portal_session_checkbox.isChecked():
            command.extend(["-restore-portal-session", "yes"])
        
        # Verbose
        command.extend(["-v", "yes" if self.verbose_checkbox.isChecked() else "no"])
        
        return command