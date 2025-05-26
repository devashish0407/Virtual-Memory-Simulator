import logging
from .address_translation import hex_to_page_offset
from .page_table import PageTable
from .memory_frames import MemoryFrames
from .replacement_algorithms import get_algorithm
from .page_fault_handler import handle_page_fault

class TLB:
    def __init__(self, size=16):
        self.size = size
        self.entries = []  # (page, frame)

    def lookup(self, page):
        for p, f in self.entries:
            if p == page:
                logging.debug(f"TLB: Hit for page {page}, frame {f}")
                return f
        logging.debug(f"TLB: Miss for page {page}")
        return None

    def update(self, page, frame):
        self.entries = [(p, f) for (p, f) in self.entries if p != page]
        self.entries.insert(0, (page, frame))
        if len(self.entries) > self.size:
            evicted = self.entries.pop()
            logging.debug(f"TLB: Evicted {evicted} from TLB")
        logging.debug(f"TLB: Updated with page {page}, frame {frame}")

    def remove(self, page):
        self.entries = [(p, f) for (p, f) in self.entries if p != page]
        logging.debug(f"TLB: Removed page {page} from TLB")

def run_simulation(trace, algorithm_name, frame_size, tlb_size=16):
    logging.debug("Simulation started")
    page_table = PageTable()
    frames = MemoryFrames(frame_size)
    algo = get_algorithm(algorithm_name, trace)
    tlb = TLB(size=tlb_size)

    result = {
        "trace": trace,
        "translation": [],
        "page_table": [],
        "frames": [],
        "page_faults": [],
        "logs": [],
        "tlb_hits": 0,
        "tlb_misses": 0,
        "detailed_trace": []
    }

    for i, line in enumerate(trace):
        try:
            parts = line.strip().split()
            if not parts:
                continue

            hex_addr = parts[0]
            access_type = parts[1] if len(parts) > 1 else "R"

            page, offset = hex_to_page_offset(hex_addr)
            page_info = page_table.access(page)
            frame = tlb.lookup(page)
            tlb_hit = False
            tlb_miss = False
            page_fault = False
            evicted = None

            if frame is not None and page_info and page_info.get("valid", False):
                # TLB hit
                result["tlb_hits"] += 1
                tlb_hit = True
                result["logs"].append(f"TLB HIT for page {page} (address {hex_addr})")
                if access_type == "W":
                    page_info["dirty"] = True
            else:
                # TLB miss or invalid page
                result["tlb_misses"] += 1
                tlb_miss = True
                result["logs"].append(f"TLB MISS for page {page} (address {hex_addr})")
                if not page_info or not page_info.get("valid", False):
                    evicted = handle_page_fault(frames, page_table, page, algo, i)
                    result["page_faults"].append({"access": hex_addr, "fault": True, "evicted": evicted})
                    result["logs"].append(f"Page fault at address {hex_addr}, evicted page: {evicted}")
                    page_fault = True
                else:
                    result["page_faults"].append({"access": hex_addr, "fault": False, "evicted": None})
                    result["logs"].append(f"Accessed valid page {page} at address {hex_addr} without fault")

                frame = page_table.table[page]["frame"]
                tlb.update(page, frame)

            # Clean up TLB if page is evicted
            if evicted is not None:
                tlb.remove(evicted)

            if algorithm_name == "LRU":
                algo.update(page)

            OFFSET_BITS = 12
            physical_address = (frame << OFFSET_BITS) + offset

            result["translation"].append({
                "virtual_address": hex_addr,
                "page": page,
                "offset": offset,
                "physical_address": hex(physical_address),
                "access_type": access_type,
                "dirty": page_table.table.get(page, {}).get("dirty", False),
                "page_fault": page_fault,
                "tlb_hit": tlb_hit,
                "tlb_miss": tlb_miss,
                "evicted": evicted
            })

            result["page_table"].append({str(k): v.copy() for k, v in page_table.table.items()})
            result["frames"].append(frames.get_frame_content().copy())

            result["detailed_trace"].append({
                "Step": i,
                "Virtual Addr": hex_addr,
                "Page": page,
                "Offset": offset,
                "Frame": frame,
                "Physical Addr": hex(physical_address),
                "Access": access_type,
                "TLB Hit": tlb_hit,
                "TLB Miss": tlb_miss,
                "Page Fault": page_fault,
                "Evicted": evicted
            })

        except Exception as e:
            logging.error(f"Error in trace line {i}: {e}")
            result["logs"].append(f"Error in trace line {i}: {e}")

    result["logs"].append(f"TLB hits: {result['tlb_hits']}, TLB misses: {result['tlb_misses']}")
    logging.debug("Simulation finished")
    return result
