import streamlit as st
import pandas as pd
import json
from simulation.simulation import run_simulation
from simulation.replacement_algorithms import algorithms_available
from simulation.statistics import get_statistics

def parse_trace_input(trace_text):
    # Parses multiline or comma separated addresses with optional access type (R/W)
    lines = trace_text.strip().splitlines()
    addresses = []
    for line in lines:
        parts = line.split(",")
        for p in parts:
            addr = p.strip()
            if addr:
                # If no access type provided, default to 'R'
                if " " not in addr:
                    addr = addr + " R"
                addresses.append(addr)
    return addresses

def validate_trace(trace):
    valid_trace = []
    for entry in trace:
        parts = entry.split()
        if len(parts) != 2:
            st.error(f"Invalid format, expected: <address> <R/W>, got: {entry}")
            continue
        addr, access = parts
        try:
            int(addr, 16)  # Validate hex address
        except ValueError:
            st.error(f"Invalid hex address: {addr}")
            continue
        if access.upper() not in ("R", "W"):
            st.error(f"Invalid access type (should be R or W): {access}")
            continue
        valid_trace.append(f"{addr} {access.upper()}")
    return valid_trace

def plot_memory_state(frames, page_table_snapshot):
    import plotly.graph_objects as go

    n = len(frames)
    colors = []
    texts = []
    for page in frames:
        if page is None:
            colors.append("lightgrey")
            texts.append("Empty")
        else:
            dirty = page_table_snapshot.get(str(page), {}).get("dirty", False)
            colors.append("red" if dirty else "green")
            texts.append(f"Page {page}\n{'Dirty' if dirty else 'Clean'}")

    fig = go.Figure(data=[go.Bar(
        x=list(range(n)),
        y=[1]*n,
        marker_color=colors,
        text=texts,
        textposition='auto',
    )])
    fig.update_layout(title="Physical Memory Frames", yaxis=dict(showticklabels=False))
    st.plotly_chart(fig)

def plot_page_table(page_table_snapshot):
    if not page_table_snapshot:
        st.write("Page table empty")
        return
    df = pd.DataFrame.from_dict(page_table_snapshot, orient='index')
    st.subheader("Page Table Snapshot")
    st.dataframe(df)

def main():
    st.title("🖥️ Virtual Memory Simulator")

    st.sidebar.header("Input Options")
    input_mode = st.sidebar.radio("Choose input mode:", ["Manual Input", "Upload File"])

    trace = []
    if input_mode == "Manual Input":
        trace_text = st.sidebar.text_area(
            "Enter virtual addresses (comma or newline separated, format: 0xADDR R/W):",
            value="0x0001 R, 0x0002 W, 0x0003 R"
        )
        trace = parse_trace_input(trace_text)

    else:  # Upload File
        uploaded_file = st.sidebar.file_uploader("Upload a trace file (.txt)", type=["txt"])
        if uploaded_file:
            content = uploaded_file.read().decode("utf-8")
            trace = parse_trace_input(content)

    trace = validate_trace(trace)

    st.sidebar.markdown("---")

    # Use only FIFO, LRU, OPT for now, exclude Random and Clock
    available_algos = [algo for algo in algorithms_available() if algo in ("FIFO", "LRU", "OPT")]
    algorithm = st.sidebar.selectbox("Select Page Replacement Algorithm:", available_algos)
    frame_size = st.sidebar.number_input("Number of Frames (Physical Memory Size):", min_value=1, max_value=10, value=3)

    start_sim = st.sidebar.button("▶️ Start Simulation")
    reset = st.sidebar.button("🔄 Reset")

    if reset:
        st.experimental_rerun()  # Clear all and restart

    # Load/Save Simulation State
    uploaded_state_file = st.sidebar.file_uploader("Load Simulation State (JSON)", type=["json"])
    saved_state = None
    if uploaded_state_file:
        saved_state = json.load(uploaded_state_file)
        st.success("Simulation state loaded!")
        # Show loaded state summary
        st.subheader("Loaded Simulation Statistics")
        st.table(pd.DataFrame([get_statistics(saved_state)]))

    if start_sim and trace:
        st.info(f"Running simulation with {algorithm} and {frame_size} frames...")
        result = run_simulation(trace, algorithm, frame_size)

        # Save simulation state for download
        state_json = json.dumps(result)

        st.sidebar.download_button(
            label="💾 Save Simulation State",
            data=state_json,
            file_name="simulation_state.json",
            mime="application/json"
        )

        # Show statistics
        stats = get_statistics(result)
        st.subheader("📊 Simulation Statistics")
        st.table(pd.DataFrame([stats]))

        # Show page faults timeline
        st.subheader("⚠️ Page Fault Events")
        faults_df = pd.DataFrame(result["page_faults"])
        st.dataframe(faults_df)

        # Step through the simulation states
        st.subheader("🧮 Step Through Simulation")
        step = st.slider("Select Step", 0, len(result["frames"]) - 1, 0)

        # Show page table and frames at selected step
        plot_memory_state(result["frames"][step], result["page_table"][step])
        plot_page_table(result["page_table"][step])

        # Show page table updates after each access
        st.subheader("📄 Page Table per Access (Summary)")
        page_table_df = pd.json_normalize(result["page_table"])
        st.dataframe(page_table_df)

        # Show frame contents after each access (Summary)
        st.subheader("🧮 Memory Frames per Access (Summary)")
        frames_df = pd.json_normalize(result["frames"])
        st.dataframe(frames_df)

        # Detailed logs
        st.subheader("📝 Simulation Logs")
        st.text_area("Step-by-step logs", value="\n".join(result.get("logs", [])), height=300)

    # Side-by-side comparison
    compare_algos = st.sidebar.checkbox("Compare FIFO, LRU, and OPT algorithms")
    if compare_algos and trace:
        st.subheader("🤼 Algorithm Comparison")

        compare_results = {}
        summary = []
        for algo in available_algos:
            res = run_simulation(trace, algo, frame_size)
            compare_results[algo] = res
            stats = get_statistics(res)
            summary.append({"Algorithm": algo, **stats})

        st.table(pd.DataFrame(summary))

if __name__ == "__main__":
    main()
