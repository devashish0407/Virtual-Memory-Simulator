def handle_page_fault(frames, page_table, page, replacement_algo, current_index=0):
    evicted = None
    free_index = frames.get_free_index()
    if free_index != -1:
        frames.load_page(free_index, page)
        page_table.update(page, free_index)
    else:
        idx_to_replace = (
            replacement_algo.evict(frames.get_frame_content(), current_index)
            if isinstance(replacement_algo, type(lambda: None)) else
            replacement_algo.evict(frames.get_frame_content())
        )
        evicted = frames.get_frame_content()[idx_to_replace]
        page_table.invalidate(evicted)
        frames.replace_page(idx_to_replace, page)
        page_table.update(page, idx_to_replace)
    return evicted
