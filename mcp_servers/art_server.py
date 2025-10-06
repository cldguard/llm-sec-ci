#!/usr/bin/env python3
import os, subprocess
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="art-mcp", version="0.1.0")

@app.get("/health")
def health():
    return {"status":"ok"}

@app.post("/run")
def run(body: dict):
    script = body.get("script","configs/art_example.py")
    os.makedirs("artifacts/art", exist_ok=True)
    out = subprocess.run(["python", script], capture_output=True, text=True, check=False)
    return {"ok": out.returncode == 0, "returncode": out.returncode, "stdout": out.stdout[-4000:], "stderr": out.stderr[-4000:], "results": "artifacts/art/results.json"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8767)