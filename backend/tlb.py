# backend/tlb.py
class TLB:
    def __init__(self, size):
        self.size = size
        self.entries = {}
        self.total_accesses = 0  # Track total accesses (hits + misses)
        self.total_hits = 0      # Track total hits

    def lookup(self, logical_address):
        self.total_accesses += 1
        if logical_address in self.entries:
            self.total_hits += 1  # <-- increment hits here
            return self.entries[logical_address]
        return None


    def add_entry(self, logical_address, frame_number):
        """Add a new entry to the TLB."""
        if len(self.entries) >= self.size:
            self.entries.pop(next(iter(self.entries)))  # Remove the first entry if TLB is full
        self.entries[logical_address] = frame_number

    def get_hit_ratio(self):
        """Calculate and return the TLB hit ratio."""
        if self.total_accesses == 0:
            return 0  # Prevent division by zero
        return self.total_hits / self.total_accesses
