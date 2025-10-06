#!/usr/bin/env python3
import os, subprocess
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="garak-mcp", version="0.1.0")

@app.get("/health")
def health():
    return {"status":"ok"}

@app.post("/scan")
def scan(target: dict):
    cfg = target.get("config_path","configs/garak.toml")
    env = os.environ.copy()
    env.update(target.get("env", {}))
    os.makedirs("artifacts/garak", exist_ok=True)
    cmd = ["garak","--config", cfg, "--output-dir","artifacts/garak","--format","json"]
    out = subprocess.run(cmd, env=env, capture_output=True, text=True, check=False)
    return {"ok": out.returncode == 0, "returncode": out.returncode, "stdout": out.stdout[-4000:], "stderr": out.stderr[-4000:], "artifacts_dir": "artifacts/garak"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8765)