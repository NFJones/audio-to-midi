from midiutil.MidiFile import MIDIFile

class MidiWriter(object):
    """
    An object which takes in a list of midi notes and generates
        a midi file from it.
    """
    
    def __init__(self, outfile, time_quantum):
        """
        MidiWriter object constructor.
        
        outfile is the file to be written to.
        time_quantum is the time window in ms.
        """
        
        self.pattern = MIDIFile(1)
        self.outfile = outfile
        self.current_tick = 0
        
        #Determine the number of ticks per note.
        self.tick_quantum = int(time_quantum/100)+1
        
    def get_pattern(self):
        """
        Accessor for the midi pattern.
        """
        
        return self.pattern
        
    def get_outfile(self):
        """
        Accessor for the output file string.
        """
        
        return self.outfile
        
    def get_current_tick(self):
        """
        Accessor for the current midi tick.
        """
        
        return self.current_tick
        
    def get_tick_quantum(self):
        """
        Accessor for the tick quantum.
        """
        
        return self.tick_quantum
        
    def set_current_tick(self, current_tick):
        """
        Mutator for the current tick.
        """
        
        self.current_tick = current_tick
        
    def add_notes(self, notes):
        """
        notes is a list of midi notes to add at the current
            time step.
            
        Adds each note in the list to the current time step
            with the volume, track and channel specified.
        """
        
        for key, val in notes.items():
            pitch = key
            volume = val['volume']
            track = val['track']
            channel = val['channel']
            time = self.get_current_tick()
            duration = self.get_tick_quantum()
            pattern = self.get_pattern()
            pattern.addNote(track,channel,pitch,time,duration,volume)
        
        self.set_current_tick(self.get_current_tick() + self.get_tick_quantum())
    
    def write_file(self):
        """
        Writes the midi pattern to the output file.
        """
        
        with open(self.get_outfile(), 'wb') as outfile:
            self.get_pattern().writeFile(outfile)