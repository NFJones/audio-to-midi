from PyQt4 import QtCore, QtGui
import sys
import os
import threading

import fftMIDI_gui
import FFT
import WavParser
from FFT import FFT

class GUI(fftMIDI_gui.Ui_fftMIDI):
    def run(self):
        app = QtGui.QApplication(sys.argv)
        MainWindow = QtGui.QMainWindow()
        
        #set default computational values
        self.time_quantum = 500
        self.activation_level = 50
        self.infile = ""
        self.outfile = os.path.dirname(os.path.realpath(__file__)) + "/temp.mid"
        self.samples = []
        self.rate = 44100
        
        self.setupUi(MainWindow)
        self.bind_actions()
        MainWindow.show()
        sys.exit(app.exec_())
        
    def bind_actions(self):
        #infile button
        self.button_infile.connect(self.button_infile, QtCore.SIGNAL('clicked()'), self.infile_change)
        self.input_infile_text.setText(str(self.infile))
        
        #outfile button
        self.button_outfile.connect(self.button_outfile, QtCore.SIGNAL('clicked()'), self.outfile_change)
        self.input_outfile_text.setText(str(self.outfile))
        
        #run button
        self.button_run.connect(self.button_run, QtCore.SIGNAL('clicked()'), self.compute)
        
        #time quantum
        self.slider_time_quantum.setValue(self.time_quantum / 10)
        self.label_time_quantum_display.setText(str(self.time_quantum) + " ms")
        self.slider_time_quantum.connect(self.slider_time_quantum, QtCore.SIGNAL('valueChanged(int)'), self.time_quantum_change)
        
        #activation level
        self.slider_activation_level.setValue(self.activation_level)
        self.label_activation_level_display.setText(str(self.activation_level) + "%")
        self.slider_activation_level.connect(self.slider_activation_level, QtCore.SIGNAL('valueChanged(int)'), self.activation_level_change)
        
    def set_run_text_error(self, text):
        self.label_run_msg.setText(QtGui.QApplication.translate("fftMIDI", "<html><head/><body><p align=\"center\"><span style=\" color:#e65c5e;\">"+text+"</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        
    def set_run_text_confirmation(self, text):
        self.label_run_msg.setText(QtGui.QApplication.translate("fftMIDI", "<html><head/><body><p align=\"center\"><span style=\" color:#67e667;\">"+text+"</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
    
    def infile_change(self):
        self.infile = QtGui.QFileDialog.getOpenFileName(caption="Open File (.wav)", filter="*.wav")
        self.input_infile_text.setText(str(self.infile))
        
    def outfile_change(self):
        self.outfile = QtGui.QFileDialog.getSaveFileName(caption="Save File (.mid)", filter="*.mid")
        
        if not self.outfile[-4:] == '.mid':
            self.outfile += '.mid'
            
        self.input_outfile_text.setText(str(self.outfile))
        
    def time_quantum_change(self):
        self.time_quantum = 10 * (self.slider_time_quantum.value() + 1)
        self.label_time_quantum_display.setText(str(self.time_quantum) + " ms")
        
    def activation_level_change(self):
        self.activation_level = self.slider_activation_level.value() + 1
        self.label_activation_level_display.setText(str(self.activation_level) + "%")
        
    def compute(self):
        try:
            if self.infile != "":
                self.set_run_text_confirmation("Running.")
                wav_thread = threading.Thread(target=self.gen_midi)
                wav_thread.start()
                wav_thread.join()
                self.set_run_text_confirmation("Done!")
            
            else:
                self.set_run_text_error("You haven't selected an input file!")
        except:
            self.set_run_text_error("Unknown Error!")
            
    def gen_midi(self):
        self.samples, self.rate = WavParser.get_samples_from_wav(str(self.infile))
        fft = FFT(self.samples, self.rate, self.time_quantum, self.activation_level, self.outfile)
        fft.calculate()
        