import streamlit as st
import json, time
from plc.engine import PLCState, scan_cycle, eval_rung
from plc.parser import load_program

st.set_page_config(page_title="PLC Simulator", layout="wide")
st.title("🪛 PLC Simulator — Ladder Logic")

uploaded = st.file_uploader("Upload Ladder JSON", type=["json"])
if uploaded:
    program = json.load(uploaded)
else:
    st.info("Load examples/demo.json to start.")
    program = None

if program:
    tags = program.get("tags", {})
    rungs = program.get("rungs", [])
    st.write("**Tags**:", tags)
    st.code(json.dumps(rungs, indent=2))

    # Control panel
    cols = st.columns(4)
    cycles = cols[0].number_input("Cycles", 1, 10000, 100)
    delay = cols[1].number_input("Delay (ms)", 0, 1000, 50)
    # live inputs
    st.subheader("Inputs")
    in_tags = [k for k in tags.keys() if k.startswith("I")]
    out_tags = [k for k in tags.keys() if k.startswith("Q")]
    mem_tags = [k for k in tags.keys() if k.startswith("M")]
    input_vals = {}
    for k in in_tags:
        input_vals[k] = st.checkbox(k, value=bool(tags[k]))

    if st.button("Run Scan"):
        st.session_state["run"] = True

    # state
    st_state = PLCState(tags)
    for k, v in input_vals.items():
        st_state.set(k, int(v))

    if st.session_state.get("run", False):
        log = st.empty()
        for i in range(int(cycles)):
            # update inputs each cycle (static here; UI could be dynamic)
            for k, v in input_vals.items():
                st_state.set(k, int(v))
            for rung in rungs:
                eval_rung(rung, st_state, 1)
            time.sleep(delay/1000.0)
            log.json(st_state.tags)
        st.session_state["run"] = False

    st.subheader("Outputs")
    st.json({k: st_state.get(k) for k in out_tags})
