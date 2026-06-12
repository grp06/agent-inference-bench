# parasail / Qwen/Qwen3.5-397B-A17B — `chat` — 2026-06-11

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
Pricing: $0.5/M input, $3.6/M output, cached input billed at 30% off.

## Summary

| metric | value |
|---|---|
| requests | 8 (0 failed, 0 rate-limit retries) |
| input tokens | 223 |
| cached input tokens | 0 (0.0%) — reported on 8/8 requests |
| output tokens | 2,048 |
| TTFT p50 / p95 | 0.42 s / 2.13 s (max; n=8) |
| latency p50 / p95 | 3.26 s / 4.89 s (max; n=8) |
| mean output tok/s | 90.1 |
| cost (list price) | $0.0075 |
| cost (cache-aware) | $0.0075 |

## Per-request detail

| # | input tok | cached | output tok | TTFT s | total s | tok/s | retries |
|---|---|---|---|---|---|---|---|
| 1 | 27 | 0 | 256 | 2.13 | 4.89 | 92.8 | 0 |
| 2 | 24 | 0 | 256 | 0.45 | 3.25 | 91.2 | 0 |
| 3 | 26 | 0 | 256 | 0.38 | 3.20 | 91.0 | 0 |
| 4 | 30 | 0 | 256 | 0.44 | 3.48 | 84.3 | 0 |
| 5 | 25 | 0 | 256 | 0.40 | 3.26 | 89.4 | 0 |
| 6 | 30 | 0 | 256 | 0.47 | 3.30 | 90.5 | 0 |
| 7 | 33 | 0 | 256 | 0.38 | 3.21 | 90.5 | 0 |
| 8 | 28 | 0 | 256 | 0.38 | 3.19 | 91.1 | 0 |
