# parasail / deepseek-ai/DeepSeek-V4-Flash — `chat` — 2026-06-11

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
Pricing: $0.14/M input, $0.28/M output, cached input billed at 30% off.

## Summary

| metric | value |
|---|---|
| requests | 8 (4 failed, 28 rate-limit retries) |
| input tokens | 84 |
| cached input tokens | 0 (0.0%) — reported on 4/4 requests |
| output tokens | 1,024 |
| TTFT p50 / p95 | 0.54 s / 20.35 s (max; n=4) |
| latency p50 / p95 | 7.49 s / 24.59 s (max; n=4) |
| mean output tok/s | 53.6 |
| cost (list price) | $0.0003 |
| cost (cache-aware) | $0.0003 |

## Per-request detail

| # | input tok | cached | output tok | TTFT s | total s | tok/s | retries |
|---|---|---|---|---|---|---|---|
| 1 | 20 | 0 | 256 | 0.51 | 10.36 | 26.0 | 4 |
| 2 | 19 | 0 | 256 | 20.35 | 24.59 | 60.3 | 4 |
| 3 | — | — | — | — | — | failed: RateLimitError: Error code: 429 - {'error': {'message': 'The engine is currently overloaded. Please try again later.', 'type': 'invalid_request_error', 'param': None, 'code': None}} | 4 |
| 4 | — | — | — | — | — | failed: RateLimitError: Error code: 429 - {'error': {'message': 'The engine is currently overloaded. Please try again later.', 'type': 'invalid_request_error', 'param': None, 'code': None}} | 4 |
| 5 | 19 | 0 | 256 | 0.44 | 4.36 | 65.4 | 0 |
| 6 | — | — | — | — | — | failed: RateLimitError: Error code: 429 - {'error': {'message': 'The engine is currently overloaded. Please try again later.', 'type': 'invalid_request_error', 'param': None, 'code': None}} | 4 |
| 7 | 26 | 0 | 256 | 0.56 | 4.63 | 62.9 | 4 |
| 8 | — | — | — | — | — | failed: RateLimitError: Error code: 429 - {'error': {'message': 'The engine is currently overloaded. Please try again later.', 'type': 'invalid_request_error', 'param': None, 'code': None}} | 4 |
