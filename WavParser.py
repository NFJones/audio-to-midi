import wave
import struct

def get_samples_from_wav(infile):
    """
    infile is the .wav file to read.
    
    Reads the .wav file and produces the left-most channel
        as a list of floating point samples.
    """
    
    wav = wave.open(infile, 'rb')
    nchannels, sampwidth, framerate, nframes, comptype, compname = wav.getparams()
    raw_frames = wav.readframes(nframes)
    frames = format_frames(raw_frames, sampwidth, nchannels)
    samples = []
    total = 0.0
    increment = 10.0 / nframes
    
    #First pass to build list.
    #24-bit
    if sampwidth == 3:
        for i in range(0, len(frames), 3):
            temp_int_1 = int(struct.unpack('<H', frames[i][0:2])[0]) & 0x00FF
            temp_int_2 = int(struct.unpack('<b', frames[i][2])[0])<<16
            
            #combine bits to form 24-bit signed int
            unpacked_int = temp_int_2 | temp_int_1
            samples.append(float(unpacked_int))
            
    #16-bit
    else:
        for frame in frames:
            samples.append(float(struct.unpack('<h', frame)[0]))
            
    wav.close()
    
    return samples, framerate

def format_frames(raw_frames, sampwidth, nchannels):
    """
    raw_frames is the list of bytes from the .wav file.
    sampwidth is the sample width in bytes.
    nchannels is the number of audio channels.
    
    Filters out all frames which do not belong to the left-most
        audio channel and returns the result.
    """
    
    frames = []
    
    #build each little-endian string and add it to frames
    for i in range(0, len(raw_frames), sampwidth * nchannels):
        temp_frame = []
        for j in range(sampwidth):
            temp_frame.append(raw_frames[i + j])
            
        #lambda to concatenate the elements within temp_frame
        frames.append(reduce(lambda x, y: x + y, temp_frame, ""))
        
    return frames
