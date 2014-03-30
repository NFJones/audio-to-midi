# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui/WAVtoMIDI.ui'
#
# Created: Sun Mar 30 14:05:30 2014
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_fftMIDI(object):
    def setupUi(self, fftMIDI):
        fftMIDI.setObjectName(_fromUtf8("fftMIDI"))
        fftMIDI.resize(431, 354)
        self.centralwidget = QtGui.QWidget(fftMIDI)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.slider_time_quantum = QtGui.QSlider(self.centralwidget)
        self.slider_time_quantum.setGeometry(QtCore.QRect(160, 100, 211, 31))
        self.slider_time_quantum.setOrientation(QtCore.Qt.Horizontal)
        self.slider_time_quantum.setObjectName(_fromUtf8("slider_time_quantum"))
        self.slider_activation_level = QtGui.QSlider(self.centralwidget)
        self.slider_activation_level.setGeometry(QtCore.QRect(160, 140, 211, 31))
        self.slider_activation_level.setOrientation(QtCore.Qt.Horizontal)
        self.slider_activation_level.setObjectName(_fromUtf8("slider_activation_level"))
        self.label_time_quantum = QtGui.QLabel(self.centralwidget)
        self.label_time_quantum.setGeometry(QtCore.QRect(80, 100, 81, 31))
        self.label_time_quantum.setObjectName(_fromUtf8("label_time_quantum"))
        self.label_activation_level = QtGui.QLabel(self.centralwidget)
        self.label_activation_level.setGeometry(QtCore.QRect(50, 140, 111, 31))
        self.label_activation_level.setObjectName(_fromUtf8("label_activation_level"))
        self.label_time_quantum_display = QtGui.QLabel(self.centralwidget)
        self.label_time_quantum_display.setGeometry(QtCore.QRect(380, 100, 51, 31))
        self.label_time_quantum_display.setObjectName(_fromUtf8("label_time_quantum_display"))
        self.label_activation_level_display = QtGui.QLabel(self.centralwidget)
        self.label_activation_level_display.setGeometry(QtCore.QRect(380, 140, 51, 31))
        self.label_activation_level_display.setObjectName(_fromUtf8("label_activation_level_display"))
        self.input_infile_text = QtGui.QLineEdit(self.centralwidget)
        self.input_infile_text.setGeometry(QtCore.QRect(160, 20, 251, 31))
        self.input_infile_text.setObjectName(_fromUtf8("input_infile_text"))
        self.input_outfile_text = QtGui.QLineEdit(self.centralwidget)
        self.input_outfile_text.setGeometry(QtCore.QRect(160, 60, 251, 31))
        self.input_outfile_text.setObjectName(_fromUtf8("input_outfile_text"))
        self.button_infile = QtGui.QPushButton(self.centralwidget)
        self.button_infile.setGeometry(QtCore.QRect(20, 20, 131, 31))
        self.button_infile.setObjectName(_fromUtf8("button_infile"))
        self.button_outfile = QtGui.QPushButton(self.centralwidget)
        self.button_outfile.setGeometry(QtCore.QRect(20, 60, 131, 31))
        self.button_outfile.setObjectName(_fromUtf8("button_outfile"))
        self.button_run = QtGui.QPushButton(self.centralwidget)
        self.button_run.setGeometry(QtCore.QRect(160, 270, 111, 31))
        self.button_run.setObjectName(_fromUtf8("button_run"))
        self.label_run_msg = QtGui.QLabel(self.centralwidget)
        self.label_run_msg.setGeometry(QtCore.QRect(0, 240, 431, 31))
        self.label_run_msg.setObjectName(_fromUtf8("label_run_msg"))
        self.radio_condense_notes = QtGui.QCheckBox(self.centralwidget)
        self.radio_condense_notes.setGeometry(QtCore.QRect(150, 170, 141, 41))
        self.radio_condense_notes.setObjectName(_fromUtf8("radio_condense_notes"))
        self.radio_single_note = QtGui.QCheckBox(self.centralwidget)
        self.radio_single_note.setGeometry(QtCore.QRect(150, 210, 161, 31))
        self.radio_single_note.setObjectName(_fromUtf8("radio_single_note"))
        self.progress_bar = QtGui.QProgressBar(self.centralwidget)
        self.progress_bar.setGeometry(QtCore.QRect(10, 240, 411, 23))
        self.progress_bar.setProperty("value", 24)
        self.progress_bar.setObjectName(_fromUtf8("progress_bar"))
        fftMIDI.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(fftMIDI)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 431, 25))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        fftMIDI.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(fftMIDI)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        fftMIDI.setStatusBar(self.statusbar)

        self.retranslateUi(fftMIDI)
        QtCore.QMetaObject.connectSlotsByName(fftMIDI)

    def retranslateUi(self, fftMIDI):
        fftMIDI.setWindowTitle(QtGui.QApplication.translate("fftMIDI", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.label_time_quantum.setText(QtGui.QApplication.translate("fftMIDI", "Resolution", None, QtGui.QApplication.UnicodeUTF8))
        self.label_activation_level.setText(QtGui.QApplication.translate("fftMIDI", "Volume Cutoff", None, QtGui.QApplication.UnicodeUTF8))
        self.label_time_quantum_display.setText(QtGui.QApplication.translate("fftMIDI", "0 ms", None, QtGui.QApplication.UnicodeUTF8))
        self.label_activation_level_display.setText(QtGui.QApplication.translate("fftMIDI", "0%", None, QtGui.QApplication.UnicodeUTF8))
        self.button_infile.setText(QtGui.QApplication.translate("fftMIDI", "Input File (WAV)", None, QtGui.QApplication.UnicodeUTF8))
        self.button_outfile.setText(QtGui.QApplication.translate("fftMIDI", "Output File (MIDI)", None, QtGui.QApplication.UnicodeUTF8))
        self.button_run.setText(QtGui.QApplication.translate("fftMIDI", "Run", None, QtGui.QApplication.UnicodeUTF8))
        self.label_run_msg.setText(QtGui.QApplication.translate("fftMIDI", "<html><head/><body><p align=\"center\"><br/></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.radio_condense_notes.setText(QtGui.QApplication.translate("fftMIDI", "Condense Notes", None, QtGui.QApplication.UnicodeUTF8))
        self.radio_single_note.setText(QtGui.QApplication.translate("fftMIDI", "Single Note Mode", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    fftMIDI = QtGui.QMainWindow()
    ui = Ui_fftMIDI()
    ui.setupUi(fftMIDI)
    fftMIDI.show()
    sys.exit(app.exec_())

