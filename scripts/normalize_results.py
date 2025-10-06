#!/usr/bin/env python3
import json, time, os
from pathlib import Path
from glob import glob

def load_json(path):
    try:
        with open(path,"r") as f: return json.load(f)
    except Exception: return None
def write_out(path, data):
    Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
    with open(path,"w") as f: json.dump(data,f,indent=2)
now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

# Promptfoo suites
for name, p in {
  "promptfoo-dvla":"artifacts/promptfoo/dvla-results.json",
  "promptfoo-recruit":"artifacts/promptfoo/recruit-results.json",
}.items():
    pf = load_json(p)
    if pf is not None:
        summary = {
            "total": pf.get("stats",{}).get("numTests") or pf.get("total", None),
            "failed": pf.get("stats",{}).get("numFailures"),
            "passed": pf.get("stats",{}).get("numPasses"),
        }
        write_out(f"artifacts/normalized/{name}.json", {"scanner":name,"timestamp":now,"summary":summary,"raw_path":p})

# Garak aggregation
for sub in ["dvla","recruit"]:
    gpaths = list(Path(f"artifacts/garak/{sub}").glob("*.json"))
    if gpaths:
        total=0; issues=0
        for p in gpaths:
            data = load_json(str(p)) or {}
            total += int(data.get("tests_total",0) or data.get("count",0) or 0)
            issues += int(data.get("issues",0) or data.get("failures",0) or 0)
        write_out(f"artifacts/normalized/garak-{sub}.json", {"scanner":f"garak-{sub}","timestamp":now,"summary":{"total":total,"issues":issues},"raw_path":f"artifacts/garak/{sub}"} )

# ART
art = load_json("artifacts/art/results.json")
if art is not None:
    write_out("artifacts/normalized/art.json", {"scanner":"art","timestamp":now,"summary":{"attacks":art.get("attacks"),"metrics":art.get("metrics")},"raw_path":"artifacts/art/results.json"})

# Trivy
trivy_summ={"critical":0,"high":0,"medium":0,"findings":0}
for p in glob("artifacts/trivy/*.json"):
    data = load_json(p) or {}
    for res in (data.get("Results") or []):
        for v in (res.get("Vulnerabilities") or []):
            sev=(v.get("Severity") or "").lower()
            if sev in trivy_summ: trivy_summ[sev]+=1
            trivy_summ["findings"]+=1
if trivy_summ["findings"]:
    write_out("artifacts/normalized/trivy.json", {"scanner":"trivy","timestamp":now,"summary":trivy_summ,"raw_path":"artifacts/trivy/"})
print("Wrote artifacts/normalized/*.json")