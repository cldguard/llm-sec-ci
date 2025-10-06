#!/usr/bin/env python3
import os, json, time, requests
from pathlib import Path
URL=os.getenv("GRAFANA_URL"); TOK=os.getenv("GRAFANA_TOKEN"); LOKI=os.getenv("LOKI_URL")
def ann(tag,summary):
    if not (URL and TOK): return
    r=requests.post(f"{URL}/api/annotations",
        headers={"Authorization":f"Bearer {TOK}","Content-Type":"application/json"},
        json={"time":int(time.time()*1000),"tags":["llm-security",tag],"text":f"{tag.upper()} summary: "+json.dumps(summary)},timeout=30)
    print("Grafana:",r.status_code, r.text[:200])
def loki(tag,summary):
    if not LOKI: return
    r=requests.post(LOKI,json={"streams":[{"stream":{"job":"llm-sec-ci","scanner":tag},"values":[[str(int(time.time()*1e9)),json.dumps(summary)]]}]} ,timeout=30)
    print("Loki:", r.status_code, r.text[:200])
def main():
    for name in ["promptfoo-dvla","promptfoo-recruit","garak-dvla","garak-recruit","art","trivy"]:
        p=Path(f"artifacts/normalized/{name}.json")
        if p.exists():
            d=json.loads(p.read_text()); s=d.get("summary",{})
            ann(name,s); loki(name,s)
if __name__=="__main__": main()