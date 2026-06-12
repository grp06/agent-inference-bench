# parasail-kimi-k26 / moonshotai/Kimi-K2.6 — `agent_loop` — 2026-06-11

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
| requests | 45 (0 failed, 2 rate-limit retries) |
| input tokens | 1,760,869 |
| cached input tokens | 1,566,896 (89.0%) — reported on 45/45 requests |
| output tokens | 8,349 |
| TTFT p50 / p95 | 1.55 s / 12.31 s |
| latency p50 / p95 | 4.98 s / 28.87 s |
| mean output tok/s | 41.8 |
| cost (list price) | $1.3499 |
| cost (cache-aware) | $0.9973 |

## Per-request detail

| # | input tok | cached | output tok | TTFT s | total s | tok/s | retries |
|---|---|---|---|---|---|---|---|
| 1 | 25,261 | 0 | 554 | 3.24 | 16.28 | 42.5 | 0 |
| 2 | 26,012 | 25,248 | 91 | 1.22 | 2.93 | 53.0 | 0 |
| 3 | 26,156 | 26,000 | 45 | 3.67 | 4.45 | 57.7 | 0 |
| 4 | 26,253 | 0 | 56 | 2.89 | 4.04 | 48.8 | 0 |
| 5 | 26,360 | 26,144 | 57 | 1.22 | 2.18 | 58.9 | 0 |
| 6 | 26,468 | 26,352 | 170 | 5.71 | 9.13 | 49.7 | 0 |
| 7 | 26,677 | 26,464 | 52 | 1.21 | 2.23 | 51.0 | 0 |
| 8 | 32,456 | 26,240 | 59 | 1.13 | 1.90 | 76.2 | 0 |
| 9 | 32,567 | 26,672 | 112 | 1.76 | 8.90 | 15.7 | 0 |
| 10 | 32,812 | 32,560 | 91 | 4.78 | 9.00 | 21.6 | 0 |
| 11 | 32,954 | 0 | 620 | 3.60 | 10.29 | 92.7 | 0 |
| 12 | 33,626 | 32,944 | 45 | 1.68 | 2.15 | 95.6 | 0 |
| 13 | 33,725 | 32,448 | 55 | 2.53 | 4.34 | 30.4 | 0 |
| 14 | 33,834 | 32,800 | 68 | 1.50 | 4.55 | 22.3 | 0 |
| 15 | 33,955 | 33,824 | 122 | 1.34 | 5.32 | 30.6 | 0 |
| 16 | 34,129 | 33,712 | 88 | 0.87 | 2.92 | 43.1 | 0 |
| 17 | 34,758 | 0 | 81 | 3.07 | 6.04 | 27.2 | 0 |
| 18 | 34,888 | 34,112 | 283 | 1.13 | 10.23 | 31.1 | 0 |
| 19 | 35,267 | 33,936 | 57 | 1.50 | 3.11 | 35.4 | 0 |
| 20 | 35,376 | 34,880 | 96 | 0.99 | 3.20 | 43.4 | 0 |
| 21 | 35,620 | 35,248 | 69 | 1.31 | 3.05 | 39.7 | 0 |
| 22 | 35,739 | 35,616 | 272 | 1.37 | 7.48 | 44.5 | 0 |
| 23 | 36,974 | 35,360 | 166 | 1.00 | 4.98 | 41.7 | 0 |
| 24 | 41,567 | 36,960 | 37 | 1.25 | 2.07 | 44.8 | 0 |
| 25 | 41,779 | 35,728 | 904 | 1.80 | 36.46 | 26.1 | 0 |
| 26 | 42,745 | 41,552 | 47 | 0.96 | 1.98 | 45.9 | 0 |
| 27 | 42,844 | 41,760 | 53 | 1.55 | 3.12 | 33.6 | 0 |
| 28 | 42,984 | 34,752 | 591 | 1.39 | 25.31 | 24.7 | 0 |
| 29 | 43,636 | 42,832 | 37 | 1.43 | 2.28 | 43.8 | 0 |
| 30 | 43,726 | 43,632 | 37 | 3.68 | 4.52 | 43.8 | 0 |
| 31 | 43,818 | 42,976 | 85 | 5.64 | 8.44 | 30.3 | 0 |
| 32 | 44,185 | 43,712 | 201 | 1.60 | 6.11 | 44.6 | 0 |
| 33 | 44,855 | 44,176 | 90 | 14.74 | 16.79 | 43.9 | 0 |
| 34 | 44,994 | 42,496 | 47 | 1.14 | 2.10 | 48.9 | 0 |
| 35 | 45,133 | 44,976 | 398 | 0.90 | 17.10 | 24.6 | 0 |
| 36 | 45,582 | 45,120 | 37 | 1.03 | 1.95 | 40.3 | 0 |
| 37 | 45,669 | 45,568 | 302 | 1.58 | 8.45 | 44.0 | 0 |
| 38 | 46,169 | 45,664 | 520 | 1.04 | 16.69 | 33.2 | 0 |
| 39 | 46,749 | 46,160 | 45 | 1.76 | 2.75 | 45.4 | 0 |
| 40 | 49,917 | 46,736 | 48 | 7.58 | 8.79 | 39.7 | 0 |
| 41 | 53,605 | 44,800 | 567 | 13.89 | 30.40 | 34.3 | 1 |
| 42 | 54,312 | 43,776 | 50 | 8.62 | 10.35 | 28.9 | 1 |
| 43 | 54,506 | 54,304 | 295 | 1.47 | 13.49 | 24.5 | 0 |
| 44 | 55,068 | 53,600 | 37 | 1.67 | 2.58 | 40.8 | 0 |
| 45 | 55,159 | 55,056 | 612 | 1.81 | 17.02 | 40.2 | 0 |
