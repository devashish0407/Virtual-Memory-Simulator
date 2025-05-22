import time

def algorithms_available():
    return ["FIFO", "LRU", "OPT"]


class FIFO:
    def __init__(self):
        self.queue = []

    def evict(self, frames):
        # Always evict the oldest page (index 0)
        return 0


class LRU:
    def __init__(self):
        self.usage = {}

    def update(self, page):
        self.usage[page] = time.time()

    def evict(self, frames):
        # Evict the least recently used page
        # frames is a list of pages currently loaded
        lru_page = min(frames, key=lambda p: self.usage.get(p, float('inf')))
        return frames.index(lru_page)


class OPT:
    def __init__(self, trace):
        self.future_trace = trace

    def evict(self, frames, current_index):
        future = self.future_trace[current_index + 1:]
        indices = {p: future.index(p) if p in future else float('inf') for p in frames}
        # Evict the page which is used farthest in future or not used at all
        farthest_page = max(frames, key=lambda p: indices[p])
        return frames.index(farthest_page)


def get_algorithm(name, trace=None):
    if name == "FIFO":
        return FIFO()
    if name == "LRU":
        return LRU()
    if name == "OPT":
        return OPT(trace)
    return FIFO()
