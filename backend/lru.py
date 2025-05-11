class LRUReplacement:
    def __init__(self, num_frames):
        self.stack = []
        self.num_frames = num_frames

    def evict(self, frame_table, page_table):
        if len(self.stack) < self.num_frames:
            return len(self.stack)
        victim = self.stack.pop(0)
        frame = frame_table.frames.index(victim)
        page_table.entries[victim].valid = False
        return frame

    def insert(self, page_number):
        if page_number in self.stack:
            self.stack.remove(page_number)
        self.stack.append(page_number)