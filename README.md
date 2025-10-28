# PLC-Simulator

A lightweight **ladder-logic PLC simulator** in Python with:
- Instruction set: **NO/NC contacts**, **coil (OTE)**, **latch/unlatch (OTL/OTU)**, **TON** (on-delay timer), **TOF**, **CTU** (count up).
- **Scan-cycle** engine (input scan → logic solve → update outputs → housekeeping).
- **Streamlit UI** for live rung execution and status lights.
- JSON-based ladder program format, plus a simple DSL.

> Great for demonstrating control logic knowledge without hardware.

---

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate  # Win: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app/ladder_ui.py
```

Load `examples/demo.json` to see timers/counters in action.

---

## Project Layout
```
PLC-Simulator/
├── app/ladder_ui.py            # Streamlit live simulator
├── plc/
│   ├── engine.py               # scan cycle & runtime state
│   ├── instructions.py         # contacts, coils, timers, counters
│   ├── parser.py               # JSON/DSL → rungs
│   └── __init__.py
├── examples/demo.json          # sample ladder program
├── tests/test_engine.py        # unit tests
├── requirements.txt
└── README.md
```

---

## Ladder JSON (example)
```json
{
  "tags": {"I0":0, "I1":0, "M0":0, "Q0":0},
  "rungs": [
    [{"NO":"I0"}, {"TON":{"tag":"T0","pt_ms":1000}}, {"OTE":"Q0"}],
    [{"NC":"I1"}, {"CTU":{"tag":"C0","preset":3}}, {"OTL":"M0"}],
    [{"NO":"M0"}, {"OTU":"M0"}]
  ]
}
```
- Each rung is a **series** of elements; use nested arrays with `"PAR"` to express **parallel** branches (A || B).
