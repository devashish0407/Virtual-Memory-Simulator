import streamlit as st
from backend.fifo import FIFOReplacement
from backend.lru import LRUReplacement
from backend.clock import ClockReplacement
from backend.page_table import PageTable
from backend.frame_table import FrameTable
from backend.tlb import TLB
import pandas as pd

# Page config
st.set_page_config(page_title="Virtual Memory Simulator", layout="wide")

# Sidebar Inputs
st.sidebar.header("Simulation Parameters")
frame_size = st.sidebar.number_input("Frame Size", min_value=1, value=4)
page_size = st.sidebar.number_input("Page Size", min_value=1, value=8)
logical_input = st.sidebar.text_input("Logical Addresses (comma-separated)", value="0,1,2,3,0,4,1,5,2,6,3,7")
algorithm = st.sidebar.selectbox("Page Replacement Algorithm", ["FIFO", "LRU", "Clock"])

# Advanced Simulation Options
st.sidebar.markdown("---")
enable_segmentation = st.sidebar.checkbox("Enable Segmentation")
enable_multilevel_paging = st.sidebar.checkbox("Enable Multilevel Paging")
segment_limit = st.sidebar.number_input("Segment Limit", min_value=1, value=5) if enable_segmentation else None

# Reset button
if st.sidebar.button("Reset"):
    st.rerun()

# Title
st.title("📘 Virtual Memory Simulator")

# Simulation Button
if st.button("▶️ Start Simulation"):
    logical_addresses = [int(x.strip()) for x in logical_input.split(",") if x.strip().isdigit()]
    if not logical_addresses:
        st.error("❌ Please provide valid logical addresses.")
    else:
        page_table = PageTable(page_size)
        frame_table = FrameTable(frame_size)
        tlb = TLB(4)

        if algorithm == "FIFO":
            replacement_algo = FIFOReplacement(frame_size)
        elif algorithm == "LRU":
            replacement_algo = LRUReplacement(frame_size)
        else:
            replacement_algo = ClockReplacement(frame_size)

        st.subheader("📂 Simulation Tabs")
        tab1, tab2, tab3 = st.tabs(["Simulation Log", "Frame & TLB Tables", "Statistics"])

        log_data = []
        tlb_hits, page_faults = 0, 0

        for logical_address in logical_addresses:
            row = {}
            row["Logical Address"] = logical_address

            if enable_segmentation:
                if logical_address >= segment_limit:
                    row["TLB Status"] = "Segmentation Fault"
                    row["Page Fault"] = "-"
                    row["TLB State"] = "-"
                    row["Frame Table State"] = "-"
                    log_data.append(row)
                    continue

            frame_number = tlb.lookup(logical_address)
            if frame_number is not None:
                row["TLB Status"] = "TLB Hit"
                tlb_hits += 1
                row["Page Fault"] = "-"
            else:
                row["TLB Status"] = "TLB Miss"
                frame_number = page_table.get_frame(logical_address)
                if frame_number is None:
                    row["Page Fault"] = "Page Fault"
                    page_faults += 1
                    frame_number = replacement_algo.evict(frame_table, page_table)
                    page_table.set_entry(logical_address, frame_number)
                    frame_table.add_page(logical_address, frame_number)
                    replacement_algo.insert(logical_address if algorithm != "Clock" else frame_number)
                else:
                    row["Page Fault"] = f"Found in Page Table → Frame {frame_number}"
                tlb.add_entry(logical_address, frame_number)

            row["TLB State"] = str(tlb.entries)
            row["Frame Table State"] = str(frame_table.frames)
            log_data.append(row)

        # Convert to DataFrame
        result_df = pd.DataFrame(log_data)

        # Display logs in tab1
        with tab1:
            st.markdown("### 📝 Simulation Log")

        # Define color mapping
        def color_status(status, kind):
            color_map = {
        "TLB Status": {
        "TLB Hit": "#0ba53ca2",  # greenish
        "TLB Miss": "#cf0f1f6e"  # reddish
        },
        "Page Fault": {
        "Page Fault": "#ee8c1563",
        "Found in Page Table →": "#5f16cd60",
        "-": "#474646AE"
        },
        "Segmentation Fault": {
        "Segmentation Fault": "#a9112a7e"
        }
        }
            for key in color_map[kind]:
                if status.startswith(key):
                    return f'background-color: {color_map[kind][key]}'
            return ''
        # Convert DataFrame to styled HTML table
        def style_row(row):
            return [
        '',
        color_status(row["TLB Status"], "TLB Status"),
        color_status(row["Page Fault"], "Page Fault"),
        '',  # TLB State
        ''   # Frame Table State
        ]

        styled_df = result_df.style.apply(lambda row: style_row(row), axis=1)
        st.dataframe(styled_df, use_container_width=True)


        # Display tables in tab2
        with tab2:
            st.markdown("### 🧠 Final Frame Table")
            st.json(frame_table.frames)

            st.markdown("### 📌 Final TLB Entries")
            st.json(tlb.entries)

        # Display stats in tab3
        with tab3:
            st.markdown("### 📊 Simulation Statistics")
            st.metric(label="Page Faults", value=page_faults)
            st.metric(label="TLB Hits", value=tlb_hits)
            hit_ratio = tlb_hits / len(logical_addresses)
            st.metric(label="TLB Hit Ratio", value=f"{hit_ratio:.2f}")
            if enable_segmentation:
                st.info("Segmentation was enabled. Addresses beyond segment limit were rejected.")
            if enable_multilevel_paging:
                st.warning("Multilevel paging is marked for future enhancement.")

