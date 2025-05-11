class FIFOReplacement:
    def __init__(self, num_frames):
        self.queue = []
        self.num_frames = num_frames

    def evict(self, frame_table, page_table):
        if len(self.queue) < self.num_frames:
            return len(self.queue)
        victim = self.queue.pop(0)
        frame = frame_table.frames.index(victim)
        page_table.entries[victim].valid = False
        return frame

    def insert(self, page_number):
        if page_number not in self.queue:
            self.queue.append(page_number)