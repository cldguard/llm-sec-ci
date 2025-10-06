#!/usr/bin/env python3
import os, subprocess
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="garak-mcp", version="0.1.0")

@app.get("/health")
def health():
    return {"status":"ok"}

@app.post("/scan")
def safe_config_path(config_path):
    # Only allow filenames (no path separators/extensions other than .toml)
    import os
    allowed_dir = os.path.abspath("configs")
    if not config_path:
        config_path = "garak.toml"
    # Remove any path components
    base_name = os.path.basename(config_path)
    # Only allow files ending in .toml
    if not base_name.endswith(".toml"):
        raise ValueError("Config file must be a .toml file")
    # Compose the final path and ensure it is within the allowed_dir
    final_path = os.path.abspath(os.path.join(allowed_dir, base_name))
    if not final_path.startswith(allowed_dir):
        raise ValueError("Invalid config path.")
    if not os.path.exists(final_path):
        raise ValueError("Config file does not exist")
    return final_path

    
def scan(target: dict):
    cfg = target.get("config_path","configs/garak.toml")
    try:
        cfg = safe_config_path(target.get("config_path"))
    except Exception as e:
        return {"ok": False, "error": str(e)}
    env = os.environ.copy()
    env.update(target.get("env", {}))
    os.makedirs("artifacts/garak", exist_ok=True)
    cmd = ["garak","--config", cfg, "--output-dir","artifacts/garak","--format","json"]
    out = subprocess.run(cmd, env=env, capture_output=True, text=True, check=False)
    return {"ok": out.returncode == 0, "returncode": out.returncode, "stdout": out.stdout[-4000:], "stderr": out.stderr[-4000:], "artifacts_dir": "artifacts/garak"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8765)