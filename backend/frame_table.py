class FrameTable:
    def __init__(self, num_frames):
        self.frames = [None] * num_frames  # Holds page numbers

    def add_page(self, page_number, frame_number):
        if 0 <= frame_number < len(self.frames):
            self.frames[frame_number] = page_number
        else:
            raise IndexError("Frame number out of bounds")

    def evict_page(self, frame_number):
        if 0 <= frame_number < len(self.frames):
            self.frames[frame_number] = None
        else:
            raise IndexError("Frame number out of bounds")

    def find_frame_by_page(self, page_number):
        try:
            return self.frames.index(page_number)
        except ValueError:
            return None
