def parse_reference_string(input_str):
    tokens = input_str.strip().split(",")
    ref_list = []
    for token in tokens:
        token = token.strip()
        if not token:
            continue
        try:
            parts = token.split()
            if len(parts) != 2:
                raise ValueError("Each entry must have an address and an operation (e.g., 0x1A R)")
            addr_str, op = parts
            op = op.upper()
            if op not in ['R', 'W']:
                raise ValueError("Operation must be 'R' (Read) or 'W' (Write)")
            
            if addr_str.startswith("0x") or addr_str.startswith("0X"):
                virt_addr = int(addr_str, 16)
            else:
                virt_addr = int(addr_str)
            
            ref_list.append( (virt_addr, op) )
        except Exception as e:
            print(f"Skipping invalid input '{token}': {e}")
            continue
    return ref_list