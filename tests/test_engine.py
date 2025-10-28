from plc.engine import PLCState, eval_rung

def test_no_nc_ote():
    st = PLCState({"I0":1,"Q0":0})
    rung = [{"NO":"I0"},{"OTE":"Q0"}]
    eval_rung(rung, st, 1)
    assert st.get("Q0") == 1
