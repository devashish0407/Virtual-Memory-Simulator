from simulator.data_structures import PageTableEntry, TLBEntry

class VirtualMemorySimulator:
    def __init__(self, virtual_mem_size_kb, physical_mem_size_kb, page_size_kb, algorithm):
        self.virtual_mem_size = virtual_mem_size_kb * 1024
        self.physical_mem_size = physical_mem_size_kb * 1024
        self.page_size = page_size_kb * 1024

        self.num_virtual_pages = self.virtual_mem_size // self.page_size
        self.num_physical_frames = self.physical_mem_size // self.page_size

        self.algorithm = algorithm

        self.page_table = [PageTableEntry() for _ in range(self.num_virtual_pages)]
        self.frames = [None] * self.num_physical_frames
        self.tlb_capacity = 4
        self.tlb = []

        self.frame_usage_queue = []
        self.frame_last_used = {}
        self.step_counter = 0

        self.log = []
        self.page_faults = 0
        self.tlb_hits = 0
        self.memory_accesses = 0

        self.future_references_vpn = []
        self.dirty_pages = set()

    def reset(self):
        self.page_table = [PageTableEntry() for _ in range(self.num_virtual_pages)]
        self.frames = [None] * self.num_physical_frames
        self.tlb = []
        self.frame_usage_queue = []
        self.frame_last_used = {}
        self.step_counter = 0
        self.log = []
        self.page_faults = 0
        self.tlb_hits = 0
        self.memory_accesses = 0
        self.dirty_pages = set()
        self.future_references_vpn = []

    def tlb_lookup(self, vpn):
        for entry in self.tlb:
            if entry.vpn == vpn and entry.valid:
                return entry.frame
        return None

    def tlb_add(self, vpn, frame):
        for i, entry in enumerate(self.tlb):
            if entry.vpn == vpn:
                self.tlb.pop(i)
                break
        self.tlb.insert(0, TLBEntry(vpn, frame))
        if len(self.tlb) > self.tlb_capacity:
            self.tlb.pop()

    def tlb_invalidate_vpn(self, vpn):
        self.tlb = [entry for entry in self.tlb if entry.vpn != vpn]

    def find_victim_frame_optimal(self, current_index_in_ref_list):
        for i, vpn_in_frame in enumerate(self.frames):
            if vpn_in_frame is None:
                return i

        furthest_use = -1
        victim_frame_idx = None
        
        for frame_index, vpn_in_frame in enumerate(self.frames):
            try:
                future_segment = self.future_references_vpn[current_index_in_ref_list + 1:]
                next_use_relative_idx = future_segment.index(vpn_in_frame)
                next_use_absolute_idx = current_index_in_ref_list + 1 + next_use_relative_idx
                
            except ValueError:
                return frame_index
            
            if next_use_absolute_idx > furthest_use:
                furthest_use = next_use_absolute_idx
                victim_frame_idx = frame_index
        return victim_frame_idx

    def select_victim_frame(self, current_index_in_ref_list=None):
        for i, frame_content in enumerate(self.frames):
            if frame_content is None:
                return i

        if self.algorithm == "FIFO":
            victim_vpn = self.frame_usage_queue.pop(0)
            victim_frame = self.frames.index(victim_vpn)
            return victim_frame
        elif self.algorithm == "LRU":
            oldest_vpn = None
            oldest_time = self.step_counter + 1

            for vpn_in_frame in self.frames:
                if vpn_in_frame is not None:
                    if vpn_in_frame in self.frame_last_used and self.frame_last_used[vpn_in_frame] < oldest_time:
                        oldest_time = self.frame_last_used[vpn_in_frame]
                        oldest_vpn = vpn_in_frame
            
            if oldest_vpn is not None:
                victim_frame = self.frames.index(oldest_vpn)
                return victim_frame
            else:
                return 0
        elif self.algorithm == "Optimal":
            return self.find_victim_frame_optimal(current_index_in_ref_list)
        else:
            victim_vpn = self.frame_usage_queue.pop(0)
            victim_frame = self.frames.index(victim_vpn)
            return victim_frame

    def simulate_step(self, virt_addr, operation, current_index_in_ref_list):
        self.memory_accesses += 1
        self.step_counter += 1

        vpn = virt_addr // self.page_size
        offset = virt_addr % self.page_size

        comments = ""
        tlb_hit = False
        page_fault = False
        frame = None

        if vpn >= self.num_virtual_pages or virt_addr >= self.virtual_mem_size:
            self.log.append({
                "Step": self.step_counter,
                "Virtual Address": f"0x{virt_addr:X}",
                "VPN": vpn,
                "Offset": offset,
                "TLB Hit/Miss": "N/A",
                "Page Table Frame": "N/A",
                "Page Fault": "N/A",
                "Dirty Bit": "N/A",
                "Shared Page": "N/A",
                "Comments": "Invalid Virtual Address (Out of bounds for Virtual Memory Size)",
                "Frames State": self.frames.copy(),
                "Page Table State": [f"{i}:{'V' if entry.valid else 'I'}{entry.frame if entry.valid else ''}" for i, entry in enumerate(self.page_table)],
                "TLB State": [(e.vpn, e.frame) for e in self.tlb]
            })
            return

        frame_from_tlb = self.tlb_lookup(vpn)
        if frame_from_tlb is not None:
            self.tlb_hits += 1
            tlb_hit = True
            frame = frame_from_tlb
            comments += "TLB hit. "
            self.tlb_add(vpn, frame)
        else:
            comments += "TLB miss. "
            pt_entry = self.page_table[vpn]

            if pt_entry.valid:
                frame = pt_entry.frame
                comments += "Page table hit. "
                self.tlb_add(vpn, frame)
            else:
                page_fault = True
                self.page_faults += 1
                comments += "Page fault! "

                victim_frame = self.select_victim_frame(current_index_in_ref_list)
                
                evicted_vpn = self.frames[victim_frame]
                if evicted_vpn is not None:
                    evicted_pt_entry = self.page_table[evicted_vpn]
                    evicted_pt_entry.valid = False
                    self.tlb_invalidate_vpn(evicted_vpn)
                    comments += f"Evicted VPN {evicted_vpn}. "

                    if self.algorithm == "FIFO" and evicted_vpn in self.frame_usage_queue:
                        self.frame_usage_queue.remove(evicted_vpn)
                    if self.algorithm == "LRU" and evicted_vpn in self.frame_last_used:
                        del self.frame_last_used[evicted_vpn]

                    if evicted_vpn in self.dirty_pages:
                        comments += "(Dirty page written back) "
                        self.dirty_pages.remove(evicted_vpn)

                self.frames[victim_frame] = vpn
                pt_entry.frame = victim_frame
                pt_entry.valid = True
                pt_entry.dirty = False
                
                if self.algorithm == "FIFO":
                    self.frame_usage_queue.append(vpn)
                elif self.algorithm == "LRU":
                    self.frame_last_used[vpn] = self.step_counter

                frame = victim_frame
                self.tlb_add(vpn, frame)

        if self.algorithm == "LRU" and frame is not None:
             self.frame_last_used[vpn] = self.step_counter

        current_pt_entry = self.page_table[vpn]
        if operation.upper() == "W":
            current_pt_entry.dirty = True
            self.dirty_pages.add(vpn)

        log_entry = {
            "Step": self.step_counter,
            "Virtual Address": f"0x{virt_addr:X}",
            "VPN": vpn,
            "Offset": offset,
            "TLB Hit/Miss": "Hit" if tlb_hit else "Miss",
            "Page Table Frame": frame,
            "Page Fault": "Yes" if page_fault else "No",
            "Dirty Bit": current_pt_entry.dirty,
            "Shared Page": current_pt_entry.shared,
            "Comments": comments.strip(),
            "Frames State": self.frames.copy(),
            "Page Table State": [f"{i}:{'V' if entry.valid else 'I'}{entry.frame if entry.valid else ''}{'D' if entry.dirty else ''}" for i, entry in enumerate(self.page_table)],
            "TLB State": [(e.vpn, e.frame) for e in self.tlb]
        }

        self.log.append(log_entry)

    def run_simulation(self, reference_string_with_ops):
        self.reset()
        self.future_references_vpn = [addr // self.page_size for (addr, op) in reference_string_with_ops]

        for i, (virt_addr, op) in enumerate(reference_string_with_ops):
            self.simulate_step(virt_addr, op, i)

    def get_stats(self):
        page_fault_rate = (self.page_faults / self.memory_accesses) if self.memory_accesses else 0
        tlb_hit_rate = (self.tlb_hits / self.memory_accesses) if self.memory_accesses else 0
        return {
            "Total Memory Accesses": self.memory_accesses,
            "Total Page Faults": self.page_faults,
            "Page Fault Rate": page_fault_rate,
            "TLB Hit Rate": tlb_hit_rate
        }