class PageTableEntry:
    def __init__(self, frame_number=None, valid=False):
        self.frame_number = frame_number
        self.valid = valid

class PageTable:
    def __init__(self, num_pages):
        self.entries = [PageTableEntry() for _ in range(num_pages)]

    def get_frame(self, page_number):
        entry = self.entries[page_number]
        return entry.frame_number if entry.valid else None

    def set_entry(self, page_number, frame_number):
        self.entries[page_number].frame_number = frame_number
        self.entries[page_number].valid = True