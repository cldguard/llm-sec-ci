# LLM-Sec-CI 🚀
[![CI](https://github.com/cldguard/llm-sec-ci/actions/workflows/llm-security.yml/badge.svg)](https://github.com/cldguard/llm-sec-ci/actions)

LLM-Sec-CI is a **CI/CD pipeline template for securing LLM agents and applications**.

## Features
- Promptfoo & Garak for red-team evals
- IBM ART for adversarial robustness
- Trivy for container & dependency scanning (JSON + SARIF upload to GitHub code scanning)
- Mock LLM for safe, reproducible CI
- Normalized results → AWS Security Hub & Grafana
- PR gating policy (warn dev→stage, fail stage→prod)

Website: https://cldguard.com