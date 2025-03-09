#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import signal
from PyQt6.QtCore import QProcess, pyqtSignal, QObject

class ProcessSignals(QObject):
    started = pyqtSignal()
    finished = pyqtSignal()
    error = pyqtSignal(str)
    output = pyqtSignal(str)

class GPUScreenRecorderProcess:
    def __init__(self):
        self.process = QProcess()
        self.signals = ProcessSignals()
        self.process.readyReadStandardOutput.connect(self._handle_stdout)
        self.process.readyReadStandardError.connect(self._handle_stderr)
        self.process.started.connect(self.signals.started)
        self.process.finished.connect(self.signals.finished)
        self.pid = None

    def start(self, command):
        try:
            self.process.start(command[0], command[1:])
            self.pid = self.process.processId()
        except Exception as e:
            self.signals.error.emit(str(e))

    def stop(self):
        if self.process.state() == QProcess.ProcessState.Running:
            self.process.terminate()
            if not self.process.waitForFinished(1000):
                self.process.kill()

    def save_replay(self):
        if self.pid:
            try:
                os.kill(self.pid, signal.SIGUSR1)
                return True
            except ProcessLookupError:
                self.signals.error.emit("Process not found. Is recording active?")
                return False
        return False

    def toggle_pause(self):
        if self.pid:
            try:
                os.kill(self.pid, signal.SIGUSR2)
                return True
            except ProcessLookupError:
                self.signals.error.emit("Process not found. Is recording active?")
                return False
        return False

    def _handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode()
        self.signals.output.emit(data)

    def _handle_stderr(self):
        data = self.process.readAllStandardError().data().decode()
        self.signals.output.emit(data)