import time
import logging

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(message)s')

def algorithms_available():
    return ["FIFO", "LRU", "OPT"]

class FIFO:
    def __init__(self):
        self.queue = []

    def evict(self, frames):
        if not self.queue:
            self.queue = frames.copy()
        page_to_remove = self.queue.pop(0)
        logging.debug(f"FIFO: Evicting page {page_to_remove}")
        return frames.index(page_to_remove)

    def update(self, page):
        if page not in self.queue:
            self.queue.append(page)

class LRU:
    def __init__(self):
        self.usage = {}

    def update(self, page):
        self.usage[page] = time.time()

    def evict(self, frames):
        try:
            lru_page = min(frames, key=lambda p: self.usage.get(p, float('inf')))
            logging.debug(f"LRU: Evicting least recently used page {lru_page}")
            return frames.index(lru_page)
        except Exception as e:
            logging.error(f"LRU: Error during eviction: {e}")
            return 0

class OPT:
    def __init__(self, trace):
        self.future_trace = [line.split()[0] for line in trace]  # Extract address only

    def evict(self, frames, current_index):
        try:
            future = self.future_trace[current_index + 1:]
            future_pages = [int(addr, 16) // 256 for addr in future]  # Convert to page numbers
            index_map = {p: (future_pages.index(p) if p in future_pages else float('inf')) for p in frames}
            evict_page = max(index_map, key=index_map.get)
            logging.debug(f"OPT: Evicting page {evict_page}")
            return frames.index(evict_page)
        except Exception as e:
            logging.error(f"OPT: Error during eviction: {e}")
            return 0

def get_algorithm(name, trace=None):
    if name == "FIFO":
        return FIFO()
    if name == "LRU":
        return LRU()
    if name == "OPT":
        return OPT(trace)
    logging.warning(f"Unknown replacement algorithm '{name}', defaulting to FIFO")
    return FIFO()