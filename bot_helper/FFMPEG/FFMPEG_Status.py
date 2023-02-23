from os.path import getsize
from bot_helper.Names import Names



class FfmpegStatus:
    def __init__(self, process, log_file, input_file, output_file, duration):
        self.process = process
        self.name = input_file.split("/")[-1]
        self.log_file = log_file
        self.input_file = input_file
        self.input_file_size = getsize(input_file)
        self.output_file = output_file
        self.duration = duration
        self.process_logs = []
    
    def input_size(self):
        return self.input_file_size
    
    def save_log(self, line):
        self.process_logs.append(line)
        return
    
    def output_size(self):
        try:
            return getsize(self.output_file)
        except:
            return 0
    
    def type(self):
        return Names.ffmpeg