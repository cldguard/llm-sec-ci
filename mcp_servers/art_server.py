#!/usr/bin/env python3
"""
Hardened FastAPI server for running approved ART scripts safely.

Changes vs original:
- Validates and canonicalizes the requested script path against an allowlisted directory.
- Disallows absolute paths, parent traversal, and non-.py files.
- Uses sys.executable (full path) instead of a partial "python" for the interpreter.
- Runs the child process with a timeout and strict error handling; no shell involved.
- Defines a Pydantic model for the request body and returns structured results.
"""
import os
import sys
import subprocess
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
import uvicorn

app = FastAPI(title="art-mcp", version="0.1.1")

ALLOWED_ROOT = Path(__file__).parent.resolve() / "configs"
DEFAULT_SCRIPT = "art_example.py"  # lives under ./configs/
ARTIFACTS_DIR = Path(__file__).parent.resolve() / "artifacts" / "art"

class RunRequest(BaseModel):
    script: Optional[str] = None  # relative to ALLOWED_ROOT

    @field_validator("script")
    @classmethod
    def validate_script(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        # Basic character allowlist to reduce weird inputs
        allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789./_-")
        if not set(v) <= allowed:
            raise ValueError("script contains disallowed characters")
        if v.startswith("/"):
            raise ValueError("absolute paths are not allowed")
        if ".." in v.split("/"):
            raise ValueError("parent traversal is not allowed")
        if not v.endswith(".py"):
            raise ValueError("script must end with .py")
        return v

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/run")
def run(req: RunRequest):
    # Determine and validate the target script path
    rel = req.script or DEFAULT_SCRIPT
    candidate = (ALLOWED_ROOT / rel).resolve()

    # Ensure script is within the allowed root
    if not str(candidate).startswith(str(ALLOWED_ROOT.resolve())):
        raise HTTPException(status_code=400, detail="script is outside the allowed directory")
    if not candidate.is_file():
        raise HTTPException(status_code=404, detail="script not found")
    if candidate.suffix != ".py":
        raise HTTPException(status_code=400, detail="only .py scripts are allowed")

    # Prepare artifacts directory
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    # Execute the script using the current interpreter (full path)
    cmd = [sys.executable, str(candidate)]
    try:
        out = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            timeout=180,               # 3 minute cap to avoid runaway jobs
            cwd=ALLOWED_ROOT,          # run with a predictable working directory
            env={                      # minimal, inherited-safe env (augment as needed)
                "PATH": os.environ.get("PATH", ""),
                "PYTHONUNBUFFERED": "1"
            },
        )
    except subprocess.TimeoutExpired as e:
        raise HTTPException(status_code=504, detail=f"script timed out after {e.timeout}s")

    # Trim very large outputs to keep response size reasonable
    tail = 4000
    result = {
        "ok": out.returncode == 0,
        "returncode": out.returncode,
        "stdout": out.stdout[-tail:] if out.stdout else "",
        "stderr": out.stderr[-tail:] if out.stderr else "",
        "results": str(ARTIFACTS_DIR / "results.json")
    }
    # Return non-2xx if the script failed to make failure visible to clients
    if out.returncode != 0:
        raise HTTPException(status_code=500, detail=result)
    return result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8767)
