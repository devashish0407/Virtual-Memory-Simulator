import streamlit as st
from backend.fifo import FIFOReplacement
from backend.lru import LRUReplacement
from backend.clock import ClockReplacement
from backend.page_table import PageTable
from backend.frame_table import FrameTable
from backend.tlb import TLB
import pandas as pd

# Set the page configuration for a better layout
st.set_page_config(page_title="Virtual Memory Simulator", layout="wide")

# Sidebar for input entries
st.sidebar.header("Enter Simulation Parameters")

frame_size = st.sidebar.number_input("Enter Frame Size", min_value=1, value=4, step=1)
page_size = st.sidebar.number_input("Enter Page Size", min_value=1, value=8, step=1)
logical_input = st.sidebar.text_input("Enter Logical Addresses (comma-separated)", value="0,1,2,3,0,4,1,5,2,6,3,7")
algorithm = st.sidebar.selectbox("Choose Page Replacement Algorithm", ["FIFO", "LRU", "Clock"])

# Add Reset Button to clear simulation
reset_button = st.sidebar.button("Reset")

# If the Reset button is clicked, reset the simulation
if reset_button:
    st.rerun()


# Main content for displaying results
st.title("Virtual Memory Simulator")

if st.button("Start Simulation"):
    # Input validation and cleaning
    logical_addresses = [int(x.strip()) for x in logical_input.split(",") if x.strip().isdigit()]

    if not logical_addresses:
        st.error("❌ Please provide valid logical addresses.")
    else:
        # Initialize components
        page_table = PageTable(page_size)
        frame_table = FrameTable(frame_size)
        tlb = TLB(4)

        # Set the replacement algorithm
        if algorithm == "FIFO":
            replacement_algo = FIFOReplacement(frame_size)
        elif algorithm == "LRU":
            replacement_algo = LRUReplacement(frame_size)
        else:
            replacement_algo = ClockReplacement(frame_size)

        st.subheader("🔍 Simulation Steps")
        tlb_hits = 0
        page_faults = 0
        log_data = []

        # Simulation loop
        for logical_address in logical_addresses:
            result = []
            result.append(f"Logical Address: {logical_address}")

            frame_number = tlb.lookup(logical_address)
            if frame_number is not None:
                result.append("✅ TLB Hit")
                tlb_hits += 1
            else:
                result.append("❌ TLB Miss.")
                frame_number = page_table.get_frame(logical_address)

                if frame_number is None:
                    result.append("💥 Page Fault!")
                    page_faults += 1
                    frame_number = replacement_algo.evict(frame_table, page_table)
                    page_table.set_entry(logical_address, frame_number)
                    frame_table.add_page(logical_address, frame_number)
                    replacement_algo.insert(logical_address if algorithm != "Clock" else frame_number)
                else:
                    result.append(f"✔️ Found in Page Table → Frame {frame_number}")

                tlb.add_entry(logical_address, frame_number)

            # Collecting the TLB and Frame Table states
            result.append(f"Updated TLB: {tlb.entries}")
            result.append(f"Frame Table: {frame_table.frames}")

            # Append the result of each logical address processing
            log_data.append(result)

        # Display results in a more user-friendly table format
        st.markdown("### Simulation Results")
        result_df = pd.DataFrame(log_data, columns=["Logical Address", "TLB Status", "Page Fault", "TLB State", "Frame Table State"])
        st.dataframe(result_df)


        # Display simulation statistics
        st.subheader("📊 Simulation Statistics")
        st.write(f"**Page Faults:** {page_faults}")
        st.write(f"**TLB Hits:** {tlb_hits}")
        hit_ratio = tlb_hits / len(logical_addresses) if logical_addresses else 0
        st.write(f"**TLB Hit Ratio:** {hit_ratio:.2f}")
