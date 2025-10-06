#!/usr/bin/env python3
import json, sys, os
from pathlib import Path
def load(p):
    try: return json.loads(Path(p).read_text())
    except: return None
def main():
    base = sys.argv[1] if len(sys.argv)>1 else os.getenv("BASE_BRANCH","")
    trivy = load("artifacts/normalized/trivy.json") or {"summary":{}}
    s = trivy.get("summary", {}); critical=int(s.get("critical",0) or 0); high=int(s.get("high",0) or 0)
    print(f"Policy Gate: base_branch={base} critical={critical} high={high}")
    if base=="stage":
        print("WARN: Allowed for dev->stage"); sys.exit(0)
    if critical>0 or high>0:
        print("FAIL: Critical/High vulnerabilities detected."); sys.exit(1)
    print("PASS: No Critical/High vulnerabilities."); sys.exit(0)
if __name__=="__main__": main()