from PyQt4 import QtCore, QtGui
import sys
import os
import threading

import WAVtoMIDI_gui
import FFT
import WavParser
from FFT import FFT

class GUI(WAVtoMIDI_gui.Ui_fftMIDI):
    """
    This object extends the fftMIDI object produced by passing the
        .ui file produced by QtDesigner through pyuic4.
    """
    
    def run(self):
        """
        Starts the GUI.
        """
        
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
        
        #Bind the gui elements to their respective methods.
        self.bind_actions()
        MainWindow.show()
        sys.exit(app.exec_())
        
    def bind_actions(self):
        """
        Binds the gui elements to their respective methods.
        """
        
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
        """
        text is the message to set.
        
        Sets the label_run_msg label to text and colors it red.
        """
        
        self.label_run_msg.setText(QtGui.QApplication.translate("fftMIDI", "<html><head/><body><p align=\"center\"><span style=\" color:#e65c5e;\">"+text+"</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        
    def set_run_text_confirmation(self, text):
        """
        text is the message to set.
        
        Sets the label_run_msg label to text and colors it green.
        """
        
        self.label_run_msg.setText(QtGui.QApplication.translate("fftMIDI", "<html><head/><body><p align=\"center\"><span style=\" color:#67e667;\">"+text+"</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
    
    def infile_change(self):
        """
        Sets the infile to the file selected by the user after 
            clicking button_infile.
        """
        
        self.infile = QtGui.QFileDialog.getOpenFileName(caption="Open File (.wav)", filter="*.wav")
        self.input_infile_text.setText(str(self.infile))
        
    def outfile_change(self):
        """
        Sets the outfile to the file selected by the user after 
            clicking button_outfile.
        """
        
        self.outfile = QtGui.QFileDialog.getSaveFileName(caption="Save File (.mid)", filter="*.mid")
        
        if not self.outfile[-4:] == '.mid':
            self.outfile += '.mid'
            
        self.input_outfile_text.setText(str(self.outfile))
        
    def time_quantum_change(self):
        """
        Sets the time quantum to 10 time the value of the slider_time_quantum value.
        """
        
        self.time_quantum = 10 * (self.slider_time_quantum.value() + 1)
        self.label_time_quantum_display.setText(str(self.time_quantum) + " ms")
        
    def activation_level_change(self):
        """
        Sets the activation level to 10 time the value of the slider_activation_level value.
        """
        
        self.activation_level = self.slider_activation_level.value() + 1
        self.label_activation_level_display.setText(str(self.activation_level) + "%")
        
    def compute(self):
        """
        Performs the .wav to .mid computations with helper objects.
        """
        
        try:
            #Check for an infile.
            if self.infile != "":
                self.gen_midi()
                self.set_run_text_confirmation("Done!")
            
            #Otherwise, set the error text.
            else:
                self.set_run_text_error("You haven't selected an input file!")
        except:
            self.set_run_text_error("Unknown Error!")
            
    def gen_midi(self):
        """
        Gets the samples from the .wav input file and uses the FFT object
            to transform them into a midi file.
        """
        
        self.samples, self.rate = WavParser.get_samples_from_wav(str(self.infile))
        fft = FFT(self.samples, self.rate, self.time_quantum, self.activation_level, self.outfile)
        fft.calculate()
        