def hex_to_page_offset(hex_addr, page_size=256):
    addr = int(hex_addr, 16)
    page_number = addr // page_size
    offset = addr % page_size
    return page_number, offset
