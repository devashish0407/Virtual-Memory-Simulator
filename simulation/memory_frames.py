import logging

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(message)s')

class MemoryFrames:
    def __init__(self, size):
        if size <= 0:
            raise ValueError("MemoryFrames: Size must be positive")
        self.frames = [None] * size
        logging.debug(f"MemoryFrames: Initialized with size {size}")

    def has_page(self, page):
        try:
            exists = page in self.frames
            logging.debug(f"MemoryFrames: Page {page} {'found' if exists else 'not found'} in frames")
            return exists
        except Exception as e:
            logging.error(f"MemoryFrames: Error checking page {page}: {e}")
            return False

    def get_free_index(self):
        try:
            free_index = self.frames.index(None)
            logging.debug(f"MemoryFrames: Found free frame at index {free_index}")
            return free_index
        except ValueError:
            logging.debug("MemoryFrames: No free frame available")
            return -1
        except Exception as e:
            logging.error(f"MemoryFrames: Error finding free frame: {e}")
            return -1

    def load_page(self, index, page):
        try:
            if index < 0 or index >= len(self.frames):
                raise IndexError(f"MemoryFrames: Index {index} out of bounds")
            logging.debug(f"MemoryFrames: Loading page {page} into frame {index}")
            self.frames[index] = page
        except Exception as e:
            logging.error(f"MemoryFrames: Error loading page {page} at index {index}: {e}")

    def replace_page(self, index, page):
        try:
            if index < 0 or index >= len(self.frames):
                raise IndexError(f"MemoryFrames: Index {index} out of bounds")
            evicted = self.frames[index]
            logging.debug(f"MemoryFrames: Replacing page {evicted} with page {page} at frame {index}")
            self.frames[index] = page
        except Exception as e:
            logging.error(f"MemoryFrames: Error replacing page at index {index}: {e}")

    def get_frame_content(self):
        try:
            return self.frames.copy()
        except Exception as e:
            logging.error(f"MemoryFrames: Error getting frame content: {e}")
            return []