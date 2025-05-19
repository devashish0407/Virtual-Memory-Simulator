import streamlit as st
from backend.fifo import FIFOReplacement
from backend.lru import LRUReplacement
from backend.page_table import PageTable
from backend.frame_table import FrameTable
from backend.tlb import TLB
import pandas as pd

# Page config
st.set_page_config(page_title="Virtual Memory Simulator", layout="wide")

# Sidebar Inputs
st.sidebar.header("Simulation Parameters")

page_size = st.sidebar.number_input("Page Size (bytes)", min_value=1, value=8)
num_frames = st.sidebar.number_input("Number of Frames", min_value=1, value=4)

logical_input = st.sidebar.text_input(
    "Logical Addresses (comma-separated, in bytes)",
    value="0, 8, 16, 4, 12, 24, 8, 0"
)

algorithm = st.sidebar.selectbox("Page Replacement Algorithm", ["FIFO", "LRU"])

# Reset button
if st.sidebar.button("Reset"):
    st.experimental_rerun()

# Title
st.title("📘 Virtual Memory Simulator")

# Run simulation
if st.button("▶️ Start Simulation"):
    # Parse logical addresses input
    logical_addresses = [x.strip() for x in logical_input.split(",") if x.strip().isdigit()]
    logical_addresses = list(map(int, logical_addresses))

    if not logical_addresses:
        st.error("❌ Please provide valid logical addresses (numbers separated by commas).")
    else:
        max_logical_address = max(logical_addresses)
        num_pages = (max_logical_address // page_size) + 1

        # Initialize backend objects
        page_table = PageTable(num_pages)
        frame_table = FrameTable(num_frames)
        tlb = TLB(size=4)

        if algorithm == "FIFO":
            replacement_algo = FIFOReplacement(num_frames)
        else:
            replacement_algo = LRUReplacement(num_frames)

        # Prepare logs and stats
        log_data = []
        tlb_hits = 0
        page_faults = 0

        for logical_address in logical_addresses:
            page_number = logical_address // page_size
            offset = logical_address % page_size

            row = {
                "Logical Address": logical_address,
                "Page Number": page_number,
                "Offset": offset,
            }

            frame_number = tlb.lookup(page_number)
            if frame_number is not None:
                # TLB Hit
                row["TLB Status"] = "Hit"
                tlb_hits += 1
                row["Page Fault"] = "-"
            else:
                # TLB Miss
                row["TLB Status"] = "Miss"
                frame_number = page_table.get_frame(page_number)

                if frame_number is None:
                    # Page fault
                    page_faults += 1
                    row["Page Fault"] = "Page Fault"

                    frame_number = replacement_algo.evict(frame_table, page_table)
                    page_table.set_entry(page_number, frame_number)
                    frame_table.add_page(page_number, frame_number)
                    replacement_algo.insert(page_number)
                else:
                    row["Page Fault"] = "No"

                tlb.add_entry(page_number, frame_number)

            row["Frame Number"] = frame_number
            row["Frame Table State"] = str(frame_table.frames)
            row["TLB Entries"] = str(tlb.entries)

            log_data.append(row)

        # Display results in tabs
        tab1, tab2, tab3 = st.tabs(["Simulation Log", "Frame & TLB Tables", "Statistics"])

        with tab1:
            st.markdown("### 📝 Simulation Log")
            df_log = pd.DataFrame(log_data)

            # Function to color the "TLB Status" and "Page Fault" columns
            def highlight_status(row):
                tlb_status = row["TLB Status"]
                page_fault = row["Page Fault"]

                tlb_color = ''
                page_fault_color = ''

                if tlb_status == "Hit":
                    tlb_color = 'background-color: #1b8f21'  # light green
                elif tlb_status == "Miss":
                    tlb_color = 'background-color: #782f2a'  # light red/pink

                if page_fault == "Page Fault":
                    page_fault_color = 'background-color: #7a5b1c'  # light orange/yellow

                return [
                    '',               # Logical Address (no color)
                    '',               # Page Number (no color)
                    '',               # Offset (no color)
                    tlb_color,        # TLB Status
                    page_fault_color,  # Page Fault
                    '',               # Frame Number
                    '',               # Frame Table State
                    '',               # TLB Entries
                ]

            styled_df = df_log.style.apply(highlight_status, axis=1)

            st.dataframe(styled_df, use_container_width=True)

        # Tab 2 - Tables
        with tab2:
            st.markdown("### 🧠 Frame Table")
            st.json(frame_table.frames)

            st.markdown("### 📌 TLB Entries")
            st.json(tlb.entries)

            st.markdown("### 📝 Simulation Log")
            df_log = pd.DataFrame(log_data)
            st.dataframe(styled_df, use_container_width=True)

        # Tab 3 - Statistics
        with tab3:
            st.markdown("### 📊 Statistics")
            st.metric("Page Faults", page_faults)
            st.metric("TLB Hits", tlb_hits)
            hit_ratio = tlb_hits / len(logical_addresses) if logical_addresses else 0
            st.metric("TLB Hit Ratio", f"{hit_ratio:.2f}")
            st.markdown("### 📝 Simulation Log")
            df_log = pd.DataFrame(log_data)
            st.dataframe(styled_df, use_container_width=True)
