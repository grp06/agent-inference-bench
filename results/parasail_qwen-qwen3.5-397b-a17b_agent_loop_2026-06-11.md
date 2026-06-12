# parasail / Qwen/Qwen3.5-397B-A17B — `agent_loop` — 2026-06-11

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
| requests | 45 (0 failed, 2 rate-limit retries) |
| input tokens | 1,789,242 |
| cached input tokens | 1,721,280 (96.2%) — reported on 45/45 requests |
| output tokens | 8,231 |
| TTFT p50 / p95 | 1.24 s / 3.10 s |
| latency p50 / p95 | 3.30 s / 15.34 s |
| mean output tok/s | 56.5 |
| cost (list price) | $0.9243 |
| cost (cache-aware) | $0.6661 |

## Per-request detail

| # | input tok | cached | output tok | TTFT s | total s | tok/s | retries |
|---|---|---|---|---|---|---|---|
| 1 | 25,659 | 0 | 554 | 3.57 | 14.52 | 50.6 | 0 |
| 2 | 26,417 | 25,344 | 91 | 1.55 | 3.30 | 52.0 | 0 |
| 3 | 26,563 | 26,400 | 45 | 0.88 | 1.91 | 43.7 | 0 |
| 4 | 26,664 | 26,400 | 56 | 1.06 | 1.95 | 63.1 | 0 |
| 5 | 26,773 | 26,400 | 57 | 1.08 | 3.53 | 23.2 | 0 |
| 6 | 26,886 | 26,400 | 170 | 1.13 | 5.43 | 39.5 | 0 |
| 7 | 27,096 | 26,400 | 52 | 1.09 | 2.94 | 28.1 | 0 |
| 8 | 32,966 | 26,928 | 59 | 1.59 | 3.96 | 24.9 | 0 |
| 9 | 33,079 | 32,736 | 112 | 2.00 | 5.05 | 36.7 | 0 |
| 10 | 33,330 | 32,736 | 91 | 0.92 | 3.73 | 32.4 | 1 |
| 11 | 33,476 | 33,264 | 620 | 1.02 | 15.69 | 42.3 | 0 |
| 12 | 34,161 | 33,264 | 45 | 1.18 | 2.46 | 35.0 | 0 |
| 13 | 34,262 | 33,792 | 55 | 1.07 | 2.49 | 38.7 | 0 |
| 14 | 34,372 | 33,792 | 68 | 1.22 | 2.60 | 49.4 | 0 |
| 15 | 34,498 | 34,320 | 122 | 0.82 | 4.28 | 35.3 | 1 |
| 16 | 34,676 | 34,320 | 88 | 1.20 | 2.90 | 51.9 | 0 |
| 17 | 35,316 | 34,320 | 81 | 1.26 | 3.25 | 40.9 | 0 |
| 18 | 35,448 | 34,848 | 283 | 1.12 | 7.66 | 43.3 | 0 |
| 19 | 35,836 | 35,376 | 57 | 1.03 | 2.55 | 37.4 | 0 |
| 20 | 35,948 | 35,376 | 96 | 1.06 | 3.75 | 35.6 | 0 |
| 21 | 36,197 | 35,904 | 69 | 1.29 | 3.49 | 31.4 | 0 |
| 22 | 36,319 | 35,904 | 272 | 1.25 | 9.18 | 34.3 | 0 |
| 23 | 37,572 | 35,904 | 166 | 1.30 | 5.61 | 38.5 | 0 |
| 24 | 42,239 | 37,488 | 37 | 1.60 | 2.53 | 39.9 | 0 |
| 25 | 42,452 | 41,712 | 904 | 1.44 | 19.58 | 49.8 | 0 |
| 26 | 43,435 | 42,240 | 47 | 1.25 | 2.06 | 57.7 | 0 |
| 27 | 43,540 | 43,296 | 53 | 1.13 | 2.04 | 58.6 | 0 |
| 28 | 43,681 | 43,296 | 591 | 1.07 | 10.58 | 62.2 | 0 |
| 29 | 44,345 | 43,296 | 37 | 1.30 | 1.81 | 73.0 | 0 |
| 30 | 44,438 | 43,824 | 37 | 1.26 | 1.85 | 62.1 | 0 |
| 31 | 44,531 | 44,352 | 85 | 1.30 | 2.26 | 88.4 | 0 |
| 32 | 44,904 | 44,352 | 201 | 1.18 | 4.00 | 71.3 | 0 |
| 33 | 45,580 | 44,880 | 90 | 1.24 | 2.38 | 78.5 | 0 |
| 34 | 45,722 | 45,408 | 47 | 1.24 | 1.77 | 90.0 | 0 |
| 35 | 45,864 | 45,408 | 398 | 1.09 | 6.04 | 80.4 | 0 |
| 36 | 46,320 | 45,408 | 37 | 1.18 | 1.59 | 89.9 | 0 |
| 37 | 46,409 | 45,936 | 302 | 1.29 | 5.11 | 79.0 | 0 |
| 38 | 46,918 | 45,936 | 402 | 1.26 | 6.49 | 76.8 | 0 |
| 39 | 47,509 | 46,464 | 45 | 1.20 | 1.76 | 80.9 | 0 |
| 40 | 50,727 | 46,992 | 48 | 1.41 | 2.01 | 81.0 | 0 |
| 41 | 54,481 | 50,688 | 567 | 1.49 | 8.98 | 75.7 | 0 |
| 42 | 55,199 | 54,384 | 50 | 1.53 | 2.19 | 75.9 | 0 |
| 43 | 55,398 | 54,912 | 295 | 1.32 | 5.28 | 74.5 | 0 |
| 44 | 55,972 | 54,912 | 37 | 1.51 | 1.87 | 101.5 | 0 |
| 45 | 56,064 | 55,968 | 612 | 4.09 | 11.21 | 85.9 | 0 |
