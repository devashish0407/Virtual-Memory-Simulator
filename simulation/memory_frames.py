class MemoryFrames:
    def __init__(self, size):
        self.frames = [None] * size

    def has_page(self, page):
        return page in self.frames

    def get_free_index(self):
        try:
            return self.frames.index(None)
        except ValueError:
            return -1

    def load_page(self, index, page):
        self.frames[index] = page

    def replace_page(self, index, page):
        self.frames[index] = page

    def get_frame_content(self):
        return self.frames.copy()
