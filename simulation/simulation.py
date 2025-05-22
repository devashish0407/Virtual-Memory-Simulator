from .address_translation import hex_to_page_offset
from .page_table import PageTable
from .memory_frames import MemoryFrames
from .replacement_algorithms import get_algorithm
from .page_fault_handler import handle_page_fault

def run_simulation(trace, algorithm_name, frame_size):
    page_table = PageTable()
    frames = MemoryFrames(frame_size)
    algo = get_algorithm(algorithm_name, trace)

    result = {
        "trace": trace,
        "translation": [],  # stores per access translation info
        "page_table": [],
        "frames": [],
        "page_faults": [],
        "logs": []
    }

    for i, line in enumerate(trace):
        # Parse trace line as: "0x0001 R" or "0x0002 W"
        parts = line.strip().split()
        hex_addr = parts[0]
        access_type = parts[1] if len(parts) > 1 else "R"  # default read if not specified

        page, offset = hex_to_page_offset(hex_addr)
        page_info = page_table.access(page)

        # On write, mark dirty bit
        if access_type == "W" and page_info and page_info.get("valid"):
            page_table.table[page]["dirty"] = True

        if not page_info or not page_info.get("valid", False):
            evicted = handle_page_fault(frames, page_table, page, algo, i)
            result["page_faults"].append({"access": hex_addr, "fault": True, "evicted": evicted})
            result["logs"].append(f"Page fault at address {hex_addr}, evicted: {evicted}")
        else:
            result["page_faults"].append({"access": hex_addr, "fault": False, "evicted": None})
            page_table.access(page)
            result["logs"].append(f"Accessed page {page} at address {hex_addr} without fault.")

        if algorithm_name == "LRU":
            algo.update(page)
        elif algorithm_name == "Clock":
            algo.update(page)

        # Calculate physical address if page valid
        physical_address = None
        if page_table.table.get(page, {}).get("valid", False):
            frame = page_table.table[page]["frame"]
            # assuming offset bits known, for example 12 bits (4 KB pages)
            OFFSET_BITS = 12
            physical_address = (frame << OFFSET_BITS) + offset

        # Save translation info
        result["translation"].append({
            "virtual_address": hex_addr,
            "page": page,
            "offset": offset,
            "physical_address": hex(physical_address) if physical_address is not None else None,
            "access_type": access_type,
            "dirty": page_table.table.get(page, {}).get("dirty", False),
            "page_fault": not page_info or not page_info.get("valid", False),
            "evicted": evicted if (not page_info or not page_info.get("valid", False)) else None
        })

        # Save snapshots for visualization
        result["page_table"].append({str(k): v.copy() for k, v in page_table.table.items()})
        result["frames"].append(frames.get_frame_content())

    return result

