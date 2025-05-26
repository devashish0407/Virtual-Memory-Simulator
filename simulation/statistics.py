import logging

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(message)s')

def get_statistics(result):
    try:
        total = len(result.get("trace", []))
        faults = len([pf for pf in result.get("page_faults", []) if pf.get("fault")])
        tlb_hits = result.get("tlb_hits", 0)
        tlb_misses = result.get("tlb_misses", 0)

        stats = {
            "Total Accesses": total,
            "Page Faults": faults,
            "Fault Rate": f"{(faults / total) * 100:.2f}%" if total > 0 else "0.00%",
            "TLB Hits": tlb_hits,
            "TLB Misses": tlb_misses,
            "TLB Hit Rate": f"{(tlb_hits / total) * 100:.2f}%" if total > 0 else "0.00%"
        }

        logging.debug(f"Statistics: Computed stats - {stats}")
        return stats

    except Exception as e:
        logging.error(f"Statistics: Error computing statistics: {e}")
        return {
            "Total Accesses": 0,
            "Page Faults": 0,
            "Fault Rate": "0.00%",
            "TLB Hits": 0,
            "TLB Misses": 0,
            "TLB Hit Rate": "0.00%"
        }