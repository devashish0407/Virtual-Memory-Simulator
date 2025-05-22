def get_statistics(result):
    total = len(result["trace"])
    faults = len([pf for pf in result["page_faults"] if pf["fault"]])
    return {
        "Total Accesses": total,
        "Page Faults": faults,
        "Fault Rate": f"{(faults / total) * 100:.2f}%"
    }
