class PageTableEntry:
    def __init__(self, frame_number=None, valid=False):
        self.frame_number = frame_number
        self.valid = valid

class PageTable:
    def __init__(self, num_pages):
        self.entries = [PageTableEntry() for _ in range(num_pages)]
    
    def get_frame(self, page_number):
        if page_number < len(self.entries):  # Ensure the page number is valid
            entry = self.entries[page_number]
            return entry.frame_number if entry.valid else None
        return None  # Page number is out of bounds
    
    def set_entry(self, page_number, frame_number):
        if page_number < len(self.entries):  # Ensure the page number is valid
            self.entries[page_number].frame_number = frame_number
            self.entries[page_number].valid = True
        else:
            raise IndexError("Page number out of bounds.")

class VirtualMemorySimulator:
    def __init__(self, num_pages, num_frames):
        self.page_table = PageTable(num_pages)
        self.frames = [None] * num_frames  # Physical memory (frames)
        self.frame_counter = 0  # For FIFO page replacement

    def access_address(self, logical_address, page_size):
        page_number = logical_address // page_size
        offset = logical_address % page_size
        
        frame = self.page_table.get_frame(page_number)
        
        if frame is None:  # Page fault occurs
            print(f"Page fault at logical address {logical_address}.")
            self.load_page(page_number)
        else:
            print(f"Accessing logical address {logical_address} (Page {page_number}, Offset {offset}).")
    
    def load_page(self, page_number):
        # FIFO page replacement: Replace the oldest page
        if self.frames[self.frame_counter] is not None:
            print(f"Evicting page {self.frames[self.frame_counter]} from frame {self.frame_counter}.")
        
        self.frames[self.frame_counter] = page_number
        self.page_table.set_entry(page_number, self.frame_counter)
        print(f"Loaded page {page_number} into frame {self.frame_counter}.")
        
        # Update frame counter for FIFO replacement
        self.frame_counter = (self.frame_counter + 1) % len(self.frames)


