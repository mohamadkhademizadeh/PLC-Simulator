import time
from typing import Dict, Any, List

class PLCState:
    def __init__(self, tags: Dict[str, int]):
        self.tags = dict(tags)  # I*, Q*, M*, T*, C* as integers
        self.timers = {}        # tag -> dict(en, start_ms, pt_ms, done)
        self.counters = {}      # tag -> dict(cv, preset, done)

    def get(self, tag: str) -> int:
        return int(self.tags.get(tag, 0))

    def set(self, tag: str, val: int):
        self.tags[tag] = int(bool(val))

    def now_ms(self):
        return int(time.time() * 1000)

def eval_element(elem: Dict[str, Any], st: PLCState, en: int) -> int:
    # Series evaluation: pass 1/0 forward
    if "NO" in elem:
        return en and st.get(elem["NO"])
    if "NC" in elem:
        return en and (1 - st.get(elem["NC"]))
    if "OTE" in elem:
        if en: st.set(elem["OTE"], 1)
        else:  st.set(elem["OTE"], 0)
        return en
    if "OTL" in elem:
        if en: st.set(elem["OTL"], 1)
        return en
    if "OTU" in elem:
        if en: st.set(elem["OTU"], 0)
        return en
    if "TON" in elem:
        cfg = elem["TON"]
        tag = cfg["tag"]; pt = int(cfg.get("pt_ms", 1000))
        t = st.timers.setdefault(tag, {"en":0, "start":0, "pt":pt, "done":0})
        if en and not t["en"]:
            t["start"] = st.now_ms()
        t["en"] = 1 if en else 0
        t["pt"] = pt
        t["done"] = 1 if (en and (st.now_ms() - t["start"] >= pt)) else 0
        st.set(tag, t["done"])
        return en
    if "TOF" in elem:
        cfg = elem["TOF"]
        tag = cfg["tag"]; pt = int(cfg.get("pt_ms", 1000))
        t = st.timers.setdefault(tag, {"en":0, "start":0, "pt":pt, "done":0})
        if en:
            t["done"] = 1
            t["en"] = 1
        else:
            if t["en"] == 1:
                # started off-delay
                rem = t.get("off_start", st.now_ms())
                if "off_start" not in t:
                    t["off_start"] = rem
                t["done"] = 1 if (st.now_ms() - t["off_start"] < pt) else 0
                if t["done"] == 0:
                    t["en"] = 0
                    t.pop("off_start", None)
            else:
                t["done"] = 0
        st.set(tag, t["done"])
        return en
    if "CTU" in elem:
        cfg = elem["CTU"]
        tag = cfg["tag"]; preset = int(cfg.get("preset", 1))
        c = st.counters.setdefault(tag, {"cv":0, "preset":preset, "done":0, "last_en":0})
        if en and not c["last_en"]:
            c["cv"] += 1
        c["preset"] = preset
        c["done"] = 1 if c["cv"] >= preset else 0
        st.set(tag, c["done"])
        c["last_en"] = 1 if en else 0
        return en
    if "PAR" in elem:
        # parallel branches: any branch passing -> 1
        branches: List[List[Dict[str,Any]]] = elem["PAR"]
        out = 0
        for br in branches:
            out = out or eval_rung(br, st, en)
        return out
    return en

def eval_rung(rung: List[Dict[str, Any]], st: PLCState, en: int=1) -> int:
    res = en
    for el in rung:
        res = eval_element(el, st, res)
    return res

def scan_cycle(program, st: PLCState, cycles=1, delay_ms=100):
    for _ in range(cycles):
        for rung in program:
            eval_rung(rung, st, 1)
        time.sleep(delay_ms/1000.0)
