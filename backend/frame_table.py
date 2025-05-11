class FrameTable:
    def __init__(self, num_frames):
        self.frames = [None] * num_frames  # Holds page numbers

    def add_page(self, page_number, frame_number):
        self.frames[frame_number] = page_number