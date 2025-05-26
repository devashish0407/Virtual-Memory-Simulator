import streamlit as st
import pandas as pd
import altair as alt

# Import core simulation logic and helper functions from their new locations
from simulator.core import VirtualMemorySimulator
from utils.input_parser import parse_reference_string
from utils.simulation_runners import run_multi_simulation, run_single_simulation
from utils.display_utils import format_frames_state

st.set_page_config(page_title="Virtual Memory Simulator", layout="wide")

st.title("📚 Virtual Memory Simulator - Interactive Learning Platform")

# --- Sidebar: Configuration Inputs ---
with st.sidebar:
    st.header("⚙️ Simulation Settings")

    virtual_mem_size = st.number_input(
        "Virtual Memory Size (KB)", min_value=1, max_value=1024*64, value=64,
        help="Set the total size of virtual memory space"
    )
    physical_mem_size = st.number_input(
        "Physical Memory Size (KB)", min_value=1, max_value=1024*64, value=16,
        help="Set the total size of physical memory"
    )
    page_size = st.number_input(
        "Page Size (KB)", min_value=1, max_value=64, value=4,
        help="Size of each page/frame"
    )

    st.markdown("---")

    st.header("🧠 Page Replacement Algorithm")
    algorithm = st.selectbox(
        "Select Algorithm", ["FIFO", "LRU", "Optimal", "Multi-Algorithm"],
        help="Choose the page replacement algorithm for simulation"
    )

    # Checkbox for parallel simulation
    trigger_parallel_simulation = False
    if algorithm == "Multi-Algorithm":
        st.subheader("⚡️ Parallel Simulation Options")
        trigger_parallel_simulation = st.checkbox(
            "Trigger Parallel Simulation for Comparison",
            value=True,
            help="Run all algorithms simultaneously to compare their statistics."
        )

    # New checkbox for Tab 2 comparison display
    st.markdown("---")
    st.header("📈 Display Options")
    show_comparison_in_tab2 = st.checkbox(
        "Show Algorithm Comparison in 'Memory Structures' Tab",
        value=False,
        help="Toggle to display the algorithm comparison statistics in Tab 2 instead of Tab 3."
    )

    st.markdown("---")

    st.header("📄 Reference String / Workload")
    workload_input = st.text_area(
        "Enter virtual addresses with R/W (comma separated), e.g., 0x1A R, 0x3F W, 42 R, 15 W",
        placeholder="e.g., 0x0000 R, 0x1000 R, 0x2000 W, 0x0000 R, 0x3000 R, 0x1000 W",
        value="0x0000 R, 0x1000 R, 0x2000 W, 0x3000 R, 0x0000 R, 0x1000 R, 0x4000 W, 0x5000 R, 0x2000 R, 0x3000 R, 0x6000 W, 0x1000 R, 0x7000 R, 0x0000 R, 0x4000 R, 0x8000 W",
        help="Enter the sequence of virtual addresses and operation (R/W) to simulate"
    )

    simulate = st.button("▶️ Run Simulation")

# --- Simulation Trigger ---
if 'sim_results' not in st.session_state:
    st.session_state.sim_results = None

if simulate:
    if not workload_input.strip():
        st.warning("Please enter the virtual address reference string with R/W operations.")
        st.session_session_results = None
    else:
        if algorithm == "Multi-Algorithm" and trigger_parallel_simulation:
            st.session_state.sim_results = run_multi_simulation(workload_input, virtual_mem_size, physical_mem_size, page_size)
        else:
            st.session_state.sim_results = {"Single_Run": run_single_simulation(workload_input, virtual_mem_size, physical_mem_size, page_size, algorithm)}


# --- Tabs display ---

tabs = st.tabs([
    "Simulation Log",
    "Memory Structures",
    "Statistics & Reports",
])

# Tab 1: Detailed Address Translation Log
with tabs[0]:
    st.subheader("📝 Address Translation Steps")
    if st.session_state.sim_results:
        sim_obj_for_log = None
        if algorithm == "Multi-Algorithm" and trigger_parallel_simulation:
            if "FIFO" in st.session_state.sim_results:
                sim_obj_for_log = st.session_state.sim_results["FIFO"]
                st.markdown("**(Showing FIFO's detailed log and frames visualization in multi-algorithm mode)**")
            else:
                sim_obj_for_log = next(iter(st.session_state.sim_results.values()))
                st.markdown(f"**(Showing {next(iter(st.session_state.sim_results.keys()))}'s detailed log and frames visualization in multi-algorithm mode)**")
        else:
            sim_obj_for_log = st.session_state.sim_results["Single_Run"]

        if sim_obj_for_log:
            df_log = pd.DataFrame(sim_obj_for_log.log)
            df_log['Physical Memory State'] = df_log['Frames State'].apply(format_frames_state)

            st.markdown("---")
            st.subheader("⬇️ Download Memory Frames Data (CSV)")

            if not df_log.empty:
                frames_df_for_csv = pd.DataFrame()
                frames_df_for_csv['Step'] = df_log['Step']
                
                max_frames = 0
                if not df_log['Frames State'].empty:
                    max_frames = max(len(fs) for fs in df_log['Frames State'])

                for i in range(max_frames):
                    frames_df_for_csv[f'Frame {i} VPN'] = df_log['Frames State'].apply(
                        lambda x: f"VPN {x[i]}" if (len(x) > i and x[i] is not None) else "Empty"
                    )

                csv = frames_df_for_csv.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Frames Data as CSV",
                    data=csv,
                    file_name="memory_frames_log.csv",
                    mime="text/csv",
                    help="Download the state of each physical memory frame at every step of the simulation."
                )
            else:
                st.info("No frames data to download. Run simulation first.")


            st.markdown("---")
            st.subheader("Visual Memory Frames (Step-by-Step)")

            if not df_log.empty:
                max_step = df_log['Step'].max()
                selected_step = st.slider(
                    "Select Step to Visualize Frames",
                    min_value=1,
                    max_value=max_step,
                    value=1,
                    help="Drag to see memory frames state at each step."
                )

                frames_at_step = df_log[df_log['Step'] == selected_step]['Frames State'].iloc[0]

                chart_data = pd.DataFrame({
                    "Frame Index": list(range(len(frames_at_step))),
                    "VPN": [f"VPN {vpn}" if vpn is not None else "Empty" for vpn in frames_at_step],
                    "Occupied": [1 if vpn is not None else 0 for vpn in frames_at_step]
                })

                chart = alt.Chart(chart_data).mark_bar().encode(
                    x=alt.X('Frame Index:O', axis=alt.Axis(title='Physical Frame Index')),
                    y=alt.Y('Occupied:Q', axis=alt.Axis(title='Frame Status', labels=False, ticks=False)),
                    color=alt.Color('VPN:N', legend=alt.Legend(title="VPN in Frame"), title='VPN (Virtual Page Number)'),
                    tooltip=['Frame Index', 'VPN']
                ).properties(
                    title=f"Memory Frames at Step {selected_step}"
                )

                text = chart.mark_text(
                    align='center',
                    baseline='middle',
                    dy=-10
                ).encode(
                    text=alt.Text('VPN:N'),
                    color=alt.value("black")
                )

                st.altair_chart(chart + text, use_container_width=True)

            else:
                st.info("No log data to visualize frames.")

            st.markdown("---")
            st.subheader("Detailed Simulation Log")
            cols_to_show = [
                "Step", "Virtual Address", "VPN", "Offset", "TLB Hit/Miss",
                "Page Table Frame", "Page Fault", "Dirty Bit", "Physical Memory State", "Comments"
            ]
            st.dataframe(df_log[cols_to_show], height=300)
        else:
            st.info("No simulation results to display.")
    else:
        st.info("Run the simulation to see detailed translation steps.")

# Tab 2: Visualization of Memory Structures
with tabs[1]:
    st.subheader("🖥️ Page Table & Frames Visualization")
    if st.session_state.sim_results:
        sim_to_visualize = None
        if algorithm == "Multi-Algorithm" and trigger_parallel_simulation:
            if "FIFO" in st.session_state.sim_results:
                sim_to_visualize = st.session_state.sim_results["FIFO"]
                st.markdown("**(Showing FIFO's final state for visualization in multi-algorithm mode)**")
            else:
                sim_to_visualize = next(iter(st.session_state.sim_results.values()))
                st.markdown(f"**(Showing {next(iter(st.session_state.sim_results.keys()))}'s final state for visualization in multi-algorithm mode)**")
        else:
            sim_to_visualize = st.session_state.sim_results["Single_Run"]

        if sim_to_visualize:
            st.markdown("---")
            st.subheader("📊 Physical Memory Frames (Final State)")
            frames_state = sim_to_visualize.frames
            df_frames = pd.DataFrame({
                "Frame Index": list(range(len(frames_state))),
                "VPN Loaded": [f"VPN {vpn}" if vpn is not None else "Empty" for vpn in frames_state]
            })
            st.dataframe(df_frames, use_container_width=True)

            st.markdown("---")
            st.subheader("📑 Page Table (Final State)")
            page_table_data = []
            for i, entry in enumerate(sim_to_visualize.page_table):
                page_table_data.append({
                    "VPN": i,
                    "Valid Bit": "V" if entry.valid else "I",
                    "Frame Number": entry.frame if entry.valid else "-",
                    "Dirty Bit": "D" if entry.dirty else "C"
                })
            df_page_table = pd.DataFrame(page_table_data)
            st.dataframe(df_page_table, use_container_width=True)

            st.markdown("---")
            st.subheader("🧩 TLB (Translation Lookaside Buffer - Final State)")
            tlb_data = []
            for entry in sim_to_visualize.tlb:
                tlb_data.append({
                    "VPN": entry.vpn,
                    "Frame Number": entry.frame,
                    "Valid Bit": "V" if entry.valid else "I"
                })
            if tlb_data:
                df_tlb = pd.DataFrame(tlb_data)
                st.dataframe(df_tlb, use_container_width=True)
            else:
                st.write("TLB is empty.")

            st.markdown("---")
            st.subheader("Short Simulation Log (Frame Operations)")
            df_log_short = pd.DataFrame(sim_to_visualize.log)
            df_log_short['Operation Details'] = df_log_short.apply(
                lambda row: f"VA: {row['Virtual Address']} -> VPN:{row['VPN']} (Frame:{row['Page Table Frame']}) - {row['TLB Hit/Miss']} / {'PF' if row['Page Fault']=='Yes' else 'No PF'} (Dirty:{'D' if row['Dirty Bit'] else 'C'})", axis=1
            )
            st.dataframe(df_log_short[['Step', 'Operation Details']], height=200, use_container_width=True)

            if show_comparison_in_tab2:
                st.markdown("---")
                st.subheader("🔄 Algorithm Performance Comparison")
                if algorithm == "Multi-Algorithm" and trigger_parallel_simulation and st.session_state.sim_results:
                    st.write("Comparing page fault rates and TLB hit ratios across different algorithms:")
                    stats_data = []
                    for algo_name, sim_obj in st.session_state.sim_results.items():
                        stats = sim_obj.get_stats()
                        stats_data.append({
                            "Algorithm": algo_name,
                            "Page Faults": stats["Total Page Faults"],
                            "Page Fault Rate (%)": round(stats['Page Fault Rate']*100, 2),
                            "TLB Hit Rate (%)": round(stats['TLB Hit Rate']*100, 2)
                        })
                    df_comparison = pd.DataFrame(stats_data)
                    st.table(df_comparison.set_index("Algorithm"))
                else:
                    st.info("Select 'Multi-Algorithm' and 'Trigger Parallel Simulation' to see comparison here.")
        else:
            st.info("No simulation results to visualize.")
    else:
        st.info("Run the simulation to visualize memory structures.")

# Tab 3: Statistics and Reports
with tabs[2]:
    st.subheader("📊 Simulation Statistics")
    if st.session_state.sim_results:
        if algorithm == "Multi-Algorithm" and trigger_parallel_simulation and not show_comparison_in_tab2:
            stats_data = []
            for algo_name, sim_obj in st.session_state.sim_results.items():
                stats = sim_obj.get_stats()
                stats_data.append({
                    "Algorithm": algo_name,
                    "Total Accesses": stats["Total Memory Accesses"],
                    "Page Faults": stats["Total Page Faults"],
                    "Page Fault Rate": f"{stats['Page Fault Rate']*100:.2f}%",
                    "TLB Hit Rate": f"{stats['TLB Hit Rate']*100:.2f}%"
                })
            df_stats = pd.DataFrame(stats_data)
            st.table(df_stats)
        elif not (algorithm == "Multi-Algorithm" and trigger_parallel_simulation and show_comparison_in_tab2):
            sim_obj = st.session_state.sim_results["Single_Run"]
            stats = sim_obj.get_stats()
            st.write(f"- **Total Memory Accesses:** {stats['Total Memory Accesses']}")
            st.write(f"- **Total Page Faults:** {stats['Total Page Faults']}")
            st.write(f"- **Page Fault Rate:** {stats['Page Fault Rate']*100:.2f}%")
            st.write(f"- **TLB Hit Rate:** {stats['TLB Hit Rate']*100:.2f}%")
        else:
             st.info("Algorithm comparison is displayed in the 'Memory Structures' tab as per your selection.")

    if not show_comparison_in_tab2:
        st.markdown("---")
        st.subheader("🔄 Algorithm Performance Comparison")
        if algorithm == "Multi-Algorithm" and trigger_parallel_simulation and st.session_state.sim_results:
            st.write("Compare the performance of different page replacement algorithms below.")
            stats_data = []
            for algo_name, sim_obj in st.session_state.sim_results.items():
                stats = sim_obj.get_stats()
                stats_data.append({
                    "Algorithm": algo_name,
                    "Page Faults": stats["Total Page Faults"],
                    "Page Fault Rate (%)": round(stats['Page Fault Rate']*100, 2),
                    "TLB Hit Rate (%)": round(stats['TLB Hit Rate']*100, 2)
                })
            df_comparison = pd.DataFrame(stats_data)
            st.table(df_comparison.set_index("Algorithm"))
        else:
            st.info("Select 'Multi-Algorithm' and check 'Trigger Parallel Simulation' to compare page fault rates and TLB hit ratios across different algorithms.")


st.markdown("""
---
*This platform is designed to help you visualize and understand virtual memory management concepts step by step. Simulation logic updates views dynamically.*
""")