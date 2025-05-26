import time
import logging

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(message)s')

class PageTable:
    def __init__(self):
        self.table = {}  # page_num -> {frame, valid, dirty, last_access}
        logging.debug("PageTable: Initialized")

    def update(self, page, frame, valid=True):
        try:
            self.table[page] = {
                "frame": frame,
                "valid": valid,
                "dirty": False,
                "last_access": time.time()
            }
            logging.debug(f"PageTable: Updated page {page} with frame {frame}, valid={valid}")
        except Exception as e:
            logging.error(f"PageTable: Error updating page {page}: {e}")

    def invalidate(self, page):
        try:
            if page in self.table:
                self.table[page]["valid"] = False
                logging.debug(f"PageTable: Invalidated page {page}")
        except Exception as e:
            logging.error(f"PageTable: Error invalidating page {page}: {e}")

    def access(self, page):
        try:
            if page in self.table:
                self.table[page]["last_access"] = time.time()
                logging.debug(f"PageTable: Accessed page {page}, refreshed last_access time")
                return self.table[page]
            else:
                logging.debug(f"PageTable: Page {page} not in table")
                return None
        except Exception as e:
            logging.error(f"PageTable: Error accessing page {page}: {e}")
            return None

    def as_dict(self):
        try:
            return {str(k): v.copy() for k, v in self.table.items()}
        except Exception as e:
            logging.error(f"PageTable: Error converting to dict: {e}")
            return {}
