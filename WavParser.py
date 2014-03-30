import wave
import struct

def get_samples_from_wav(inFile):
    wav = wave.open(inFile, 'rb')
    nchannels, sampwidth, framerate, nframes, comptype, compname = wav.getparams()
    raw_frames = wav.readframes(nframes)
    frames = format_frames(raw_frames, sampwidth, nchannels)
    samples = []
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
    frames = []
    #build each little-endian string and add it to frames
    for i in range(0, len(raw_frames), sampwidth * nchannels):
        temp_frame = []
        for j in range(sampwidth):
            temp_frame.append(raw_frames[i + j])
        #lambda to concatenate the elements within temp_frame
        frames.append(reduce(lambda x, y: x + y, temp_frame, ""))
    return frames
