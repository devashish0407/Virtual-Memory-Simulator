import time

class PageTable:
    def __init__(self):
        self.table = {}  # page_num -> {frame, valid, dirty, last_access}

    def update(self, page, frame, valid=True):
        self.table[page] = {
            "frame": frame,
            "valid": valid,
            "dirty": False,
            "last_access": time.time()
        }

    def invalidate(self, page):
        if page in self.table:
            self.table[page]["valid"] = False

    def access(self, page):
        if page in self.table:
            self.table[page]["last_access"] = time.time()
        return self.table.get(page, None)

    def as_dict(self):
        return {str(k): v for k, v in self.table.items()}
