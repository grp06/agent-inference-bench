# parasail-qwen35-35b / Qwen/Qwen3.5-35B-A3B — `chat` — 2026-06-11

Harness: [agent-inference-bench](https://github.com/grp06/agent-inference-bench)

## Conditions

Single sequential run against `https://api.parasail.io/v1` from a residential network in San Francisco
on the date above. No warmup requests discarded, no concurrency, no
statistical claims — one honest sample of what a developer would see.
TTFT counts the first generated token, reasoning or visible content,
whichever arrives first. SDK retries are disabled; the one exception
is HTTP 429 (rate limit), retried with backoff and disclosed in the
retries column — timing always reflects the successful attempt only.
Failed requests are excluded from token totals and cost, so actual
billed spend can be slightly higher than the figures below.
Token counts come from the provider's reported usage.
Pricing: $0.15/M input, $1.0/M output, cached input billed at 30% off.

## Summary

| metric | value |
|---|---|
| requests | 8 (0 failed, 0 rate-limit retries) |
| input tokens | 223 |
| cached input tokens | 0 (0.0%) — reported on 8/8 requests |
| output tokens | 2,048 |
| TTFT p50 / p95 | 0.29 s / 0.70 s (max; n=8) |
| latency p50 / p95 | 1.69 s / 2.13 s (max; n=8) |
| mean output tok/s | 182.5 |
| cost (list price) | $0.0021 |
| cost (cache-aware) | $0.0021 |

## Per-request detail

| # | input tok | cached | output tok | TTFT s | total s | tok/s | retries |
|---|---|---|---|---|---|---|---|
| 1 | 27 | 0 | 256 | 0.70 | 2.13 | 178.5 | 0 |
| 2 | 24 | 0 | 256 | 0.39 | 1.92 | 167.1 | 0 |
| 3 | 26 | 0 | 256 | 0.34 | 1.62 | 199.7 | 0 |
| 4 | 30 | 0 | 256 | 0.23 | 1.61 | 185.4 | 0 |
| 5 | 25 | 0 | 256 | 0.32 | 1.60 | 199.7 | 0 |
| 6 | 30 | 0 | 256 | 0.26 | 1.60 | 190.5 | 0 |
| 7 | 33 | 0 | 256 | 0.26 | 1.76 | 170.8 | 0 |
| 8 | 28 | 0 | 256 | 0.25 | 1.77 | 168.5 | 0 |
