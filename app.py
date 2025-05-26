# app.py

import streamlit as st
import pandas as pd
import json
import logging
from simulation.simulation import run_simulation
from simulation.replacement_algorithms import algorithms_available
from simulation.statistics import get_statistics

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

def parse_trace_input(trace_text):
    lines = trace_text.strip().splitlines()
    addresses = []
    for line in lines:
        parts = line.split(",")
        for p in parts:
            addr = p.strip()
            if addr:
                if " " not in addr:
                    addr += " R"
                addresses.append(addr)
    return addresses

def validate_trace(trace):
    valid_trace = []
    errors_found = False
    for entry in trace:
        parts = entry.split()
        if len(parts) != 2:
            st.error(f"Invalid format, expected: <address> <R/W>, got: {entry}")
            errors_found = True
            continue
        addr, access = parts
        try:
            int(addr, 16)
        except ValueError:
            st.error(f"Invalid hex address: {addr}")
            errors_found = True
            continue
        if access.upper() not in ("R", "W"):
            st.error(f"Invalid access type (should be R or W): {access}")
            errors_found = True
            continue
        valid_trace.append(f"{addr} {access.upper()}")
    if errors_found and not valid_trace:
        st.error("No valid trace entries found. Please fix errors above.")
    return valid_trace

def plot_memory_state(frames, page_table_snapshot):
    import plotly.graph_objects as go
    colors = []
    texts = []
    for frame_index, page in enumerate(frames):
        if page is None:
            colors.append("lightgrey")
            texts.append("Empty")
        else:
            # Fix: Always convert page number to string when accessing snapshot
            info = page_table_snapshot.get(str(page), {})
            dirty = info.get("dirty", False)
            colors.append("red" if dirty else "green")
            texts.append(f"Page {page} ({'Dirty' if dirty else 'Clean'})")
    fig = go.Figure(data=[go.Bar(
        x=[f"Frame {i}" for i in range(len(frames))],
        y=[1]*len(frames),
        marker_color=colors,
        text=texts,
        textposition='auto',
    )])
    fig.update_layout(title="Memory Frame State", yaxis=dict(showticklabels=False))
    st.plotly_chart(fig)


def plot_page_table(page_table_snapshot):
    try:
        if not page_table_snapshot:
            st.info("Page table is empty.")
            return
        df = pd.DataFrame.from_dict(page_table_snapshot, orient='index')
        df.reset_index(inplace=True)
        df.rename(columns={"index": "Page Number"}, inplace=True)
        st.dataframe(df)
    except Exception as e:
        st.error(f"Error plotting page table: {e}")
        logging.error(f"Page table plot error: {e}")

def main():
    st.title("🧠 Virtual Memory Simulator with TLB")

    st.sidebar.header("Configuration")
    input_mode = st.sidebar.radio("Input Mode", ["Manual", "Upload File"])

    trace = []
    if input_mode == "Manual":
        trace_text = st.sidebar.text_area("Input Virtual Addresses (0xADDR R/W):", "0x0001 R, 0x0002 W, 0x0003 R")
        trace = parse_trace_input(trace_text)
    else:
        uploaded_file = st.sidebar.file_uploader("Upload trace file (.txt)", type="txt")
        if uploaded_file:
            content = uploaded_file.read().decode("utf-8")
            trace = parse_trace_input(content)

    trace = validate_trace(trace)

    algorithm = st.sidebar.selectbox("Page Replacement Algorithm", algorithms_available())
    frame_size = st.sidebar.number_input("Frame Count", min_value=1, max_value=10, value=3)
    tlb_size = st.sidebar.number_input("TLB Size", min_value=1, max_value=64, value=16)

    run = st.sidebar.button("Run Simulation")
    if run and trace:
        try:
            result = run_simulation(trace, algorithm, frame_size, tlb_size)
            stats = get_statistics(result)
            st.subheader("📊 Statistics")
            st.table(pd.DataFrame([stats]))

            st.subheader("⚠️ Page Fault Events")
            if result.get("page_faults"):
                st.dataframe(pd.DataFrame(result["page_faults"]))

            st.subheader("🧮 Simulation Step Viewer")
            if not result["frames"] or not result["page_table"]:
                st.error("Simulation did not generate valid memory frame or page table data.")
                return
            max_step = min(len(result["frames"]), len(result["page_table"])) - 1
            if max_step < 0:
                st.warning("No valid steps to display.")
                return
            step = st.slider("Step", 0, max_step, 0)
            
            if step < len(result["frames"]) and step < len(result["page_table"]):
                plot_memory_state(result["frames"][step], result["page_table"][step])
                plot_page_table(result["page_table"][step])
            else:
                st.warning("Selected step data is not available.")

            st.subheader("📝 Access Log")
            show_step_log = st.checkbox("Show Logs Up to This Step")
            logs = result.get("logs", [])
            if show_step_log:
                logs_to_show = logs[:step+1]
            else:
                logs_to_show = logs

            if logs_to_show:
                for log in logs_to_show:
                    if "Page fault" in log:
                        st.markdown(f"🔴 **{log}**")
                    elif "TLB HIT" in log:
                        st.markdown(f"🟢 {log}")
                    elif "TLB MISS" in log:
                        st.markdown(f"🟡 {log}")
                    else:
                        st.write(log)
            else:
                st.info("No logs to show.")

            st.subheader("🔍 Detailed Access Trace")
            df_trace = pd.DataFrame(result.get("detailed_trace", []))
            st.dataframe(df_trace)

        except Exception as e:
            st.error(f"Simulation error: {e}")
            logging.error(f"App: Error during simulation: {e}")

if __name__ == "__main__":
    main()
