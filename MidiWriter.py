from midiutil.MidiFile import MIDIFile

class MidiWriter(object):
    def __init__(self, outfile, time_quantum):
        self.pattern = MIDIFile(1)
        self.outfile = outfile
        self.current_tick = 0
        self.tick_quantum = int(time_quantum/100)+1
        
    def get_pattern(self):
        return self.pattern
        
    def get_outfile(self):
        return self.outfile
        
    def get_current_tick(self):
        return self.current_tick
        
    def get_tick_quantum(self):
        return self.tick_quantum
        
    def set_current_tick(self, current_tick):
        self.current_tick = current_tick
        
    def add_notes(self, notes):
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
        outfile = open(self.get_outfile(), 'wb')
        self.get_pattern().writeFile(outfile)
        outfile.close()