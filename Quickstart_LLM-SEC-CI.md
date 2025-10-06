
# Quickstart — Running LLM-Sec-CI Against Any Cloned LLM Project

This guide explains how to use the **LLM-Sec-CI Target Runner** scripts to run security and evaluation scans against any cloned LLM repository using the LLM-Sec-CI bundle.

---

## 1. Prerequisites

Install and configure the following before running:

- Docker Desktop or Docker Engine (running)
- Python 3.11+
- Node.js 20+
- Tools on PATH:
  - `trivy` (container & filesystem scanning)
  - `promptfoo` (LLM evaluation harness)
  - `garak` (LLM red-team probing)
  - `python` (to run bundle scripts)
- (Optional) `jq` (for bash) and `gh` (GitHub CLI)

To verify environment (Windows):
```powershell
.\scripts\windows\Verify-Env.ps1
.\scripts\windows\Verify-Extras.ps1
```

---

## 2. Paths

**Target repo:** cloned LLM project, e.g. `C:\code\my-llm-app`  
**LLM-Sec-CI bundle root:** location of your bundle, e.g. `llm-sec-ci_app\cline\llm-sec-ci`.

---

## 3. Target Profile

Each repo scanned by LLM-Sec-CI needs a lightweight config at:
```
<target-repo>/.llm-sec-ci/target.config.json
```

Example:
```json
{
  "name": "my-llm-app",
  "composeFile": "docker-compose.yml",
  "serviceUrls": { "app": "http://127.0.0.1:5000", "ui": "http://127.0.0.1:8501" },
  "imageName": "my-llm-app:local",
  "fsScan": true,
  "promptfooConfig": ".github/promptfoo/app-promptfoo.yaml",
  "garakConfig": ".github/garak/garak-app.toml",
  "artScript": "",
  "env": { "OPENAI_API_KEY": "mock", "OPENAI_BASE_URL": "http://127.0.0.1:8000" }
}
```

Use `New-TargetProfile.ps1` to scaffold this automatically.

---

## 4. Windows Quickstart (PowerShell)

```powershell
$TargetRoot = "C:\code\my-llm-app"
$LLMSecRoot = "llm-sec-ci_app\cline\llm-sec-ci"
$BaseBranch = "main"

# Scaffold config if needed
.\scripts\windows\runtime\New-TargetProfile.ps1 -TargetRoot $TargetRoot

# Start app stack (if docker-compose present)
.\scripts\windows\runtime\Start-Target.ps1 -TargetRoot $TargetRoot

# Run scans (Trivy, Promptfoo, Garak, ART)
.\scripts\windows\runtime\Invoke-LLMSecScan.ps1 -TargetRoot $TargetRoot -LLMSecRoot $LLMSecRoot

# Normalize outputs
.\scripts\windows\runtime\Convert-Normalize.ps1 -TargetRoot $TargetRoot -LLMSecRoot $LLMSecRoot

# Run policy gate
.\scripts\windows\runtime\Invoke-PolicyGate.ps1 -LLMSecRoot $LLMSecRoot -BaseBranch $BaseBranch

# Optional: Export to Security Hub / Grafana
.\scripts\windows\runtime\Export-Findings.ps1 -LLMSecRoot $LLMSecRoot

# Stop stack
.\scripts\windows\runtime\Stop-Target.ps1 -TargetRoot $TargetRoot
```

**One-liner orchestrator:**
```powershell
.\scripts\windows\runtime\Run-LLMSecCI.ps1 -TargetRoot "C:\code\my-llm-app" -LLMSecRoot "llm-sec-ci_app\cline\llm-sec-ci" -BaseBranch "main"
```

---

## 5. macOS / Linux Quickstart

```bash
chmod +x scripts/bash/run-llm-sec-ci.sh
export LLMSEC_ROOT="llm-sec-ci_app/cline/llm-sec-ci"
export BASE_BRANCH="main"
scripts/bash/run-llm-sec-ci.sh /Users/alex/code/my-llm-app
```

---

## 6. Outputs

| Location | Description |
|-----------|--------------|
| `<repo>/.llm-sec-ci/artifacts/` | Raw outputs (Trivy, Promptfoo, Garak, ART) |
| `<LLMSEC_ROOT>/artifacts/normalized/` | Normalized summaries |
| Console | Policy gate results (PASS/FAIL) |

---

## 7. Optional Environment Variables

To enable exports to AWS/Grafana, set:
```
AWS_ACCOUNT_ID, AWS_REGION
GRAFANA_URL, GRAFANA_TOKEN, LOKI_URL
```

Scripts no-op gracefully if unset.

---

## 8. Troubleshooting

| Issue | Resolution |
|-------|-------------|
| Ports unavailable | Check `docker compose logs` for target repo |
| Tool missing | Install with `choco`, `brew`, or manual download |
| No normalized results | Ensure raw artifacts exist first |
| Gate fails unexpectedly | Inspect normalized JSON in `artifacts/normalized` |

---

## 9. Safety Rules

- Always display full STDOUT/STDERR for any tool execution.
- Never fabricate JSON artifacts when a tool fails. Stop, show errors, and fix root cause.

---

## 10. End-to-End Summary

1. Clone your target repo.  
2. Scaffold `.llm-sec-ci/target.config.json`.  
3. Start the app (if applicable).  
4. Run scans → normalize → gate.  
5. Optionally export to dashboards.  
6. Stop the app.

```powershell
.\scripts\windows\runtime\Run-LLMSecCI.ps1 -TargetRoot "C:\code\target" -LLMSecRoot "llm-sec-ci_app\cline\llm-sec-ci" -BaseBranch main
```
```bash
scripts/bash/run-llm-sec-ci.sh /Users/alex/code/target
```

---

© CloudGuard Corp — LLM-Sec-CI Security Pipeline Quickstart
