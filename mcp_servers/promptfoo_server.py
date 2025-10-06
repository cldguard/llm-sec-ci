#!/usr/bin/env python3
import os, subprocess
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="promptfoo-mcp", version="0.1.0")

@app.get("/health")
def health():
    return {"status":"ok"}

@app.post("/eval")
def eval(body: dict):
    cfg = body.get("config","configs/promptfooconfig.yaml")
    # Only allow filenames (no path components, no slashes, no "..", no abs paths)
    import os
    if os.path.isabs(cfg) or ".." in cfg or "/" in cfg or "\\" in cfg:
        return {"ok": False, "error": "Invalid config filename."}
    config_path = os.path.join("configs", cfg) if not cfg.startswith("configs/") else cfg
    if not (config_path.endswith(".yaml") or config_path.endswith(".yml")):
        return {"ok": False, "error": "Config file must end with .yaml or .yml"}
        
    env = os.environ.copy()
    env.update(body.get("env", {}))
    os.makedirs("artifacts/promptfoo", exist_ok=True)
    cmd = ["promptfoo","eval","-c", config_path, "--json", "--output", "artifacts/promptfoo/results.json"]
    out = subprocess.run(cmd, env=env, capture_output=True, text=True, check=False)
    return {"ok": out.returncode == 0, "returncode": out.returncode, "stdout": out.stdout[-4000:], "stderr": out.stderr[-4000:], "results": "artifacts/promptfoo/results.json"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8766)