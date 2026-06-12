# parasail-kimi-k26 / moonshotai/Kimi-K2.6 — `chat` — 2026-06-11

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
Pricing: $0.75/M input, $3.5/M output, cached input billed at 30% off.

## Summary

| metric | value |
|---|---|
| requests | 8 (0 failed, 0 rate-limit retries) |
| input tokens | 201 |
| cached input tokens | 0 (0.0%) — reported on 8/8 requests |
| output tokens | 2,048 |
| TTFT p50 / p95 | 0.31 s / 0.68 s (max; n=8) |
| latency p50 / p95 | 6.20 s / 9.99 s (max; n=8) |
| mean output tok/s | 48.1 |
| cost (list price) | $0.0073 |
| cost (cache-aware) | $0.0073 |

## Per-request detail

| # | input tok | cached | output tok | TTFT s | total s | tok/s | retries |
|---|---|---|---|---|---|---|---|
| 1 | 24 | 0 | 256 | 0.68 | 7.95 | 35.2 | 0 |
| 2 | 22 | 0 | 256 | 0.32 | 3.40 | 83.1 | 0 |
| 3 | 22 | 0 | 256 | 0.27 | 4.49 | 60.7 | 0 |
| 4 | 28 | 0 | 256 | 0.27 | 9.99 | 26.4 | 0 |
| 5 | 23 | 0 | 256 | 0.31 | 4.30 | 64.2 | 0 |
| 6 | 26 | 0 | 256 | 0.37 | 9.47 | 28.2 | 0 |
| 7 | 30 | 0 | 256 | 0.35 | 6.34 | 42.7 | 0 |
| 8 | 26 | 0 | 256 | 0.29 | 6.06 | 44.4 | 0 |
