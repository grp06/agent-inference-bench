# parasail-qwen35-35b / Qwen/Qwen3.5-35B-A3B — `agent_loop` — 2026-06-11

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
| requests | 45 (0 failed, 0 rate-limit retries) |
| input tokens | 1,789,242 |
| cached input tokens | 1,712,832 (95.7%) — reported on 45/45 requests |
| output tokens | 8,349 |
| TTFT p50 / p95 | 1.16 s / 1.38 s |
| latency p50 / p95 | 1.61 s / 4.45 s |
| mean output tok/s | 185.5 |
| cost (list price) | $0.2767 |
| cost (cache-aware) | $0.1997 |

## Per-request detail

| # | input tok | cached | output tok | TTFT s | total s | tok/s | retries |
|---|---|---|---|---|---|---|---|
| 1 | 25,659 | 0 | 554 | 1.40 | 4.45 | 181.8 | 0 |
| 2 | 26,417 | 25,344 | 91 | 0.89 | 1.42 | 173.1 | 0 |
| 3 | 26,563 | 26,400 | 45 | 0.90 | 1.19 | 153.9 | 0 |
| 4 | 26,664 | 26,400 | 56 | 0.88 | 1.28 | 140.2 | 0 |
| 5 | 26,773 | 26,400 | 57 | 1.05 | 1.20 | 377.0 | 0 |
| 6 | 26,886 | 26,400 | 170 | 0.91 | 1.94 | 164.3 | 0 |
| 7 | 27,096 | 26,400 | 52 | 0.93 | 1.22 | 181.6 | 0 |
| 8 | 32,966 | 26,400 | 59 | 1.22 | 1.52 | 200.3 | 0 |
| 9 | 33,079 | 32,736 | 112 | 1.02 | 1.72 | 159.6 | 0 |
| 10 | 33,330 | 32,736 | 91 | 1.12 | 1.61 | 184.9 | 0 |
| 11 | 33,476 | 32,736 | 620 | 1.02 | 4.45 | 181.1 | 0 |
| 12 | 34,161 | 32,736 | 45 | 1.22 | 1.76 | 83.0 | 0 |
| 13 | 34,262 | 33,792 | 55 | 1.06 | 1.38 | 174.2 | 0 |
| 14 | 34,372 | 33,792 | 68 | 1.08 | 1.46 | 181.9 | 0 |
| 15 | 34,498 | 33,792 | 122 | 1.34 | 2.06 | 170.1 | 0 |
| 16 | 34,676 | 33,792 | 88 | 1.18 | 1.61 | 205.7 | 0 |
| 17 | 35,316 | 33,792 | 81 | 1.22 | 1.67 | 179.3 | 0 |
| 18 | 35,448 | 34,848 | 283 | 1.24 | 2.82 | 179.3 | 0 |
| 19 | 35,836 | 34,848 | 57 | 1.14 | 1.43 | 196.3 | 0 |
| 20 | 35,948 | 34,848 | 96 | 1.20 | 1.84 | 151.4 | 0 |
| 21 | 36,197 | 35,904 | 69 | 1.12 | 1.56 | 154.7 | 0 |
| 22 | 36,319 | 35,904 | 272 | 1.03 | 2.58 | 176.1 | 0 |
| 23 | 37,572 | 35,904 | 166 | 1.17 | 2.09 | 179.5 | 0 |
| 24 | 42,239 | 36,960 | 37 | 1.19 | 1.38 | 201.5 | 0 |
| 25 | 42,452 | 41,184 | 904 | 1.25 | 6.96 | 158.5 | 0 |
| 26 | 43,435 | 42,240 | 47 | 1.16 | 1.44 | 163.4 | 0 |
| 27 | 43,540 | 43,296 | 53 | 1.24 | 1.53 | 180.1 | 0 |
| 28 | 43,681 | 43,296 | 591 | 1.29 | 4.46 | 186.6 | 0 |
| 29 | 44,345 | 43,296 | 37 | 1.52 | 2.01 | 75.0 | 0 |
| 30 | 44,438 | 43,296 | 37 | 1.09 | 1.37 | 130.4 | 0 |
| 31 | 44,531 | 44,352 | 85 | 1.19 | 1.61 | 206.8 | 0 |
| 32 | 44,904 | 44,352 | 201 | 1.16 | 2.29 | 177.4 | 0 |
| 33 | 45,580 | 44,352 | 90 | 1.17 | 1.69 | 172.1 | 0 |
| 34 | 45,722 | 45,408 | 47 | 1.06 | 1.24 | 264.9 | 0 |
| 35 | 45,864 | 45,408 | 398 | 1.17 | 3.13 | 203.8 | 0 |
| 36 | 46,320 | 45,408 | 37 | 1.10 | 1.26 | 229.1 | 0 |
| 37 | 46,409 | 45,408 | 302 | 1.07 | 2.49 | 213.7 | 0 |
| 38 | 46,918 | 45,408 | 520 | 1.15 | 3.84 | 193.6 | 0 |
| 39 | 47,509 | 46,464 | 45 | 1.18 | 1.34 | 274.3 | 0 |
| 40 | 50,727 | 46,464 | 48 | 1.15 | 1.37 | 224.1 | 0 |
| 41 | 54,481 | 50,688 | 567 | 1.29 | 3.99 | 209.5 | 0 |
| 42 | 55,199 | 53,856 | 50 | 1.26 | 1.55 | 170.9 | 0 |
| 43 | 55,398 | 54,912 | 295 | 1.24 | 3.05 | 163.4 | 0 |
| 44 | 55,972 | 54,912 | 37 | 1.15 | 1.31 | 230.8 | 0 |
| 45 | 56,064 | 55,968 | 612 | 1.17 | 4.45 | 186.5 | 0 |
