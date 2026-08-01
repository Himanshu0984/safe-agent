# 🛡️ Safe-Agent

![Evaluation](https://github.com/Himanshu0984/safe-agent/actions/workflows/evaluate.yml/badge.svg)

A production-grade AI agent with layered guardrails, evaluation suite, and automated CI/CD.

## 🎯 What It Does

Answers questions about company projects by retrieving data from mock Gmail, Notion, and Jira — with active defenses against prompt injection, PII leakage, and hallucination.

## 📊 Evaluation Results

| Metric | Score |
|---|---|
| Accuracy | 100% (10/10 tests) |
| Adversarial Refusal Rate | 3/3 blocked |
| PII Protection | 100% |
| Avg Latency | 0.42s |

## 🛡️ Guardrails Implemented

- **Input Guardrail** — 2-layer defense (keyword filter + LLM classifier) against prompt injection
- **PII Redaction** — Microsoft Presidio catches emails, phones, names
- **Citation Enforcement** — Every fact must cite its source
- **Grounding** — Refuses to answer without evidence

## 🏗️ Architecture
     User Question
          ↓
🛡️ Input Guardrail
          ↓
[Decompose] → Sub-questions
          ↓
[Retrieve] → Gmail / Notion / Jira
          ↓
[Answer with citations]
          ↓
🛡️ PII Redaction
          ↓
[Synthesize] Final Answer


## 🧪 Continuous Evaluation

Every push triggers automated evaluation via **GitHub Actions**. See `.github/workflows/evaluate.yml`.

## 🛠️ Tech Stack

- Python 3.11
- Groq (LLM inference)
- Microsoft Presidio (PII detection)
- GitHub Actions (CI/CD)

## 🚀 Run Locally

```bash
pip install groq python-dotenv presidio-analyzer presidio-anonymizer
python -m spacy download en_core_web_sm
python full_agent.py

📝 Author
Built by Himanshu as a learning project in AI safety and evaluation.