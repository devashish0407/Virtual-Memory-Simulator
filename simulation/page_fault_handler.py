import logging

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(message)s')

def handle_page_fault(frames, page_table, page, replacement_algo, current_index=0):
    try:
        evicted = None
        free_index = frames.get_free_index()

        if free_index != -1:
            frames.load_page(free_index, page)
            page_table.update(page, free_index)
            logging.debug(f"PageFaultHandler: Loaded page {page} into free frame {free_index}")
        else:
            # Choose page to replace
            if hasattr(replacement_algo, 'evict'):
                frame_content = frames.get_frame_content()
                if 'OPT' in replacement_algo.__class__.__name__:
                    idx_to_replace = replacement_algo.evict(frame_content, current_index)
                else:
                    idx_to_replace = replacement_algo.evict(frame_content)
            else:
                raise Exception("Replacement algorithm missing 'evict' method")

            evicted = frames.get_frame_content()[idx_to_replace]
            page_table.invalidate(evicted)
            frames.replace_page(idx_to_replace, page)
            page_table.update(page, idx_to_replace)
            logging.debug(f"PageFaultHandler: Replaced page {evicted} with page {page} at frame {idx_to_replace}")

        return evicted

    except Exception as e:
        logging.error(f"PageFaultHandler: Error handling page fault for page {page}: {e}")
        return None