class PageTableEntry:
    def __init__(self):
        self.frame = None
        self.valid = False
        self.dirty = False
        self.shared = False

class TLBEntry:
    def __init__(self, vpn, frame):
        self.vpn = vpn
        self.frame = frame
        self.valid = True