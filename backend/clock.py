class ClockReplacement:
    def __init__(self, num_frames):
        self.num_frames = num_frames
        self.pages = [None] * num_frames
        self.ref_bits = [0] * num_frames
        self.pointer = 0

    def evict(self, frame_table, page_table):
        while True:
            if self.pages[self.pointer] is None:
                return self.pointer
            if self.ref_bits[self.pointer] == 0:
                victim = self.pages[self.pointer]
                page_table.entries[victim].valid = False
                return self.pointer
            self.ref_bits[self.pointer] = 0
            self.pointer = (self.pointer + 1) % self.num_frames

    def insert(self, page_number, frame_number):
        self.pages[frame_number] = page_number
        self.ref_bits[frame_number] = 1