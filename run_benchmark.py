# /// script
# requires-python = ">=3.10"
# dependencies = ["openai>=1.40", "pyyaml>=6"]
# ///
"""Replay a workload against an OpenAI-compatible endpoint and measure TTFT,
throughput, latency percentiles, and dollar cost.

    uv run run_benchmark.py --provider parasail --workload workloads/chat.jsonl [--dry-run]

Providers live in providers.yaml. Keys come from the environment or a .env
file. Requests are sequential: agent loops are sequential by nature, and
this is a fidelity benchmark, not a load test.
"""

import argparse
import datetime
import json
import os
import statistics
import sys
import time
from dataclasses import dataclass

import yaml
from openai import OpenAI, RateLimitError


@dataclass
class Provider:
    name: str
    base_url: str
    model: str
    input_per_m: float
    output_per_m: float
    api_key_env: str
    cached_discount: float | None = None


@dataclass
class RequestResult:
    index: int
    ttft_s: float | None = None
    total_s: float | None = None
    input_tokens: int = 0
    cached_tokens: int | None = None
    output_tokens: int = 0
    usage_source: str = "api"
    retries: int = 0
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None

    @property
    def gen_tok_s(self) -> float | None:
        if not self.ok or self.ttft_s is None or self.total_s is None:
            return None
        gen_time = self.total_s - self.ttft_s
        if gen_time <= 0 or self.output_tokens <= 0:
            return None
        return self.output_tokens / gen_time


def load_env_file(path: str = ".env") -> None:
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key, value = key.strip(), value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def load_provider(config_path: str, name: str) -> Provider:
    with open(config_path) as f:
        config = yaml.safe_load(f)
    if name not in config:
        sys.exit(f"error: provider '{name}' not found in {config_path} "
                 f"(available: {', '.join(config)})")
    entry = config[name]
    provider = Provider(
        name=name,
        base_url=entry["base_url"],
        model=entry["model"],
        input_per_m=float(entry["input_per_m"]),
        output_per_m=float(entry["output_per_m"]),
        api_key_env=entry["api_key_env"],
        cached_discount=entry.get("cached_discount"),
    )
    if provider.input_per_m == 0 or provider.output_per_m == 0:
        print(f"warning: pricing for '{name}' has a zero entry; "
              f"cost figures will be wrong until it is filled in", file=sys.stderr)
    return provider


def load_workload(path: str) -> list[dict]:
    requests = []
    with open(path) as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            req = json.loads(line)
            if "messages" not in req:
                sys.exit(f"error: {path}:{i} has no 'messages' field")
            requests.append(req)
    if not requests:
        sys.exit(f"error: workload {path} is empty")
    return requests


def estimate_tokens(text: str) -> int:
    return len(text) // 4


RATE_LIMIT_ATTEMPTS = 5
RATE_LIMIT_BACKOFF_S = [3, 6, 12, 24]


def run_request(client, model: str, req: dict, index: int) -> RequestResult:
    # 429s are retried with backoff and disclosed; timing restarts per attempt.
    # Everything else fails immediately (SDK retries are off).
    result = RequestResult(index=index)
    for attempt in range(RATE_LIMIT_ATTEMPTS):
        result.error = None
        try:
            _attempt_request(client, model, req, result)
            return result
        except RateLimitError as e:
            result.error = f"{type(e).__name__}: {e}"
            if attempt < RATE_LIMIT_ATTEMPTS - 1:
                backoff = RATE_LIMIT_BACKOFF_S[min(attempt, len(RATE_LIMIT_BACKOFF_S) - 1)]
                print(f"    429 on request {index}, retrying in {backoff}s "
                      f"(attempt {attempt + 2}/{RATE_LIMIT_ATTEMPTS})")
                time.sleep(backoff)
                result.retries += 1
        except Exception as e:
            result.error = f"{type(e).__name__}: {e}"
            return result
    return result


def _attempt_request(client, model: str, req: dict, result: RequestResult) -> None:
    messages = req["messages"]
    max_tokens = req.get("max_tokens", 512)
    start = time.perf_counter()
    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        stream=True,
        stream_options={"include_usage": True},
        temperature=0.2,
    )
    first_token_at = None
    generated_chars = 0
    usage = None
    for chunk in stream:
        if chunk.usage is not None:
            usage = chunk.usage
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta
        content = (getattr(delta, "content", None) or
                   getattr(delta, "reasoning_content", None) or
                   getattr(delta, "reasoning", None) or "")
        if content:
            if first_token_at is None:
                first_token_at = time.perf_counter()
            generated_chars += len(content)
    end = time.perf_counter()

    result.total_s = end - start
    result.ttft_s = (first_token_at - start) if first_token_at else None
    if usage is not None:
        result.input_tokens = usage.prompt_tokens or 0
        result.output_tokens = usage.completion_tokens or 0
        details = getattr(usage, "prompt_tokens_details", None)
        result.cached_tokens = getattr(details, "cached_tokens", None) if details else None
        result.usage_source = "api"
    else:
        result.input_tokens = estimate_tokens(str(messages))
        result.output_tokens = generated_chars // 4
        result.cached_tokens = None
        result.usage_source = "estimated"


def percentile(values: list[float], p: float) -> tuple[float | None, str]:
    # Never extrapolate past the data: under 20 samples, p95 is just the max.
    if not values:
        return None, ""
    if p == 50:
        return statistics.median(values), ""
    if len(values) < 20:
        return max(values), f" (max; n={len(values)})"
    return statistics.quantiles(values, n=100)[int(p) - 1], ""


def aggregate(results: list[RequestResult], provider: Provider) -> dict:
    ok = [r for r in results if r.ok]
    ttfts = [r.ttft_s for r in ok if r.ttft_s is not None]
    totals = [r.total_s for r in ok if r.total_s is not None]
    speeds = [s for r in ok if (s := r.gen_tok_s) is not None]
    input_tokens = sum(r.input_tokens for r in ok)
    output_tokens = sum(r.output_tokens for r in ok)
    cached_count = sum(1 for r in ok if r.cached_tokens is not None)
    cached_tokens = sum(min(r.cached_tokens or 0, r.input_tokens) for r in ok)
    cached_reported = cached_count > 0
    estimated_count = sum(1 for r in ok if r.usage_source == "estimated")

    list_cost = (input_tokens * provider.input_per_m +
                 output_tokens * provider.output_per_m) / 1e6
    cache_aware_cost = None
    if cached_reported and provider.cached_discount is not None:
        uncached = input_tokens - cached_tokens
        cache_aware_cost = (
            uncached * provider.input_per_m
            + cached_tokens * provider.input_per_m * (1 - provider.cached_discount)
            + output_tokens * provider.output_per_m
        ) / 1e6

    p50_ttft, _ = percentile(ttfts, 50)
    p95_ttft, p95_ttft_note = percentile(ttfts, 95)
    p50_total, _ = percentile(totals, 50)
    p95_total, p95_total_note = percentile(totals, 95)

    return {
        "requests": len(results),
        "failed": len(results) - len(ok),
        "input_tokens": input_tokens,
        "cached_tokens": cached_tokens if cached_reported else None,
        "cached_count": cached_count,
        "ok_count": len(ok),
        "cache_pct": (round(100 * cached_tokens / input_tokens, 1)) if cached_reported and input_tokens else None,
        "estimated_count": estimated_count,
        "output_tokens": output_tokens,
        "p50_ttft": p50_ttft,
        "p95_ttft": p95_ttft,
        "p95_ttft_note": p95_ttft_note,
        "p50_total": p50_total,
        "p95_total": p95_total,
        "p95_total_note": p95_total_note,
        "mean_tok_s": statistics.mean(speeds) if speeds else None,
        "total_retries": sum(r.retries for r in results),
        "list_cost": list_cost,
        "cache_aware_cost": cache_aware_cost,
        "usage_source": ("api" if ok and estimated_count == 0 else "estimated"),
    }


def git_commit_short() -> str:
    try:
        import subprocess
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                              capture_output=True, text=True, timeout=5).stdout.strip()
    except Exception:
        return ""


def fmt_s(value: float | None, note: str = "") -> str:
    return f"{value:.2f} s{note}" if value is not None else "n/a"


def write_markdown(summary: dict, results: list[RequestResult],
                   provider: Provider, workload_path: str, out_dir: str,
                   network_note: str, partial: bool) -> str:
    date = datetime.date.today().isoformat()
    model_short = provider.model.lower().replace("/", "-").replace(" ", "-")
    workload_stem = os.path.splitext(os.path.basename(workload_path))[0]
    suffix = "_partial" if partial else ""
    out_path = os.path.join(out_dir, f"{provider.name}_{model_short}_{workload_stem}_{date}{suffix}.md")

    if summary["cached_tokens"] is not None:
        cache_line = (f"| cached input tokens | {summary['cached_tokens']:,}"
                      f" ({summary['cache_pct']}%)"
                      f" — reported on {summary['cached_count']}/{summary['ok_count']} requests |")
    else:
        cache_line = "| cached input tokens | not reported by provider |"
    est_marker = " (ESTIMATED)" if summary["usage_source"] != "api" else ""
    cost_line = (f"| cost (cache-aware) | ${summary['cache_aware_cost']:.4f}{est_marker} |"
                 if summary["cache_aware_cost"] is not None
                 else "| cost (cache-aware) | n/a — cached tokens not reported or no discount configured |")
    if summary["usage_source"] == "api":
        usage_sentence = "Token counts come from the provider's reported usage."
    elif summary["estimated_count"] < summary["ok_count"]:
        usage_sentence = (f"Usage data was missing on {summary['estimated_count']} of "
                          f"{summary['ok_count']} requests; token counts for those are "
                          f"ESTIMATED from character counts.")
    else:
        usage_sentence = ("Token counts are ESTIMATED from character counts because "
                          "the provider did not return usage data.")
    mean_tok_s = (f"{summary['mean_tok_s']:.1f}"
                  if summary["mean_tok_s"] is not None else "n/a")

    lines = [
        f"# {provider.name} / {provider.model} — `{workload_stem}` — {date}",
        "",
        f"Harness: [agent-inference-bench](https://github.com/grp06/agent-inference-bench)"
        + (f" @ `{c}`" if (c := git_commit_short()) else ""),
        "",
        "## Conditions",
        "",
        f"Single sequential run against `{provider.base_url}` from {network_note}",
        "on the date above. No warmup requests discarded, no concurrency, no",
        "statistical claims — one honest sample of what a developer would see.",
        "TTFT counts the first generated token, reasoning or visible content,",
        "whichever arrives first. SDK retries are disabled; the one exception",
        "is HTTP 429 (rate limit), retried with backoff and disclosed in the",
        "retries column — timing always reflects the successful attempt only.",
        "Failed requests are excluded from token totals and cost, so actual",
        "billed spend can be slightly higher than the figures below.",
        usage_sentence,
        f"Pricing: ${provider.input_per_m}/M input, ${provider.output_per_m}/M output"
        + (f", cached input billed at {round(provider.cached_discount * 100)}% off."
           if provider.cached_discount is not None else "."),
    ]
    if partial:
        lines.append("")
        lines.append("**PARTIAL RUN**: the replay was interrupted; this file covers "
                     "only the requests completed before the interruption.")
    lines += [
        "",
        "## Summary",
        "",
        "| metric | value |",
        "|---|---|",
        f"| requests | {summary['requests']} ({summary['failed']} failed, "
        f"{summary['total_retries']} rate-limit retries) |",
        f"| input tokens | {summary['input_tokens']:,} |",
        cache_line,
        f"| output tokens | {summary['output_tokens']:,} |",
        f"| TTFT p50 / p95 | {fmt_s(summary['p50_ttft'])} / {fmt_s(summary['p95_ttft'], summary['p95_ttft_note'])} |",
        f"| latency p50 / p95 | {fmt_s(summary['p50_total'])} / {fmt_s(summary['p95_total'], summary['p95_total_note'])} |",
        f"| mean output tok/s | {mean_tok_s} |",
        f"| cost (list price) | ${summary['list_cost']:.4f}{est_marker} |",
        cost_line,
        "",
        "## Per-request detail",
        "",
        "| # | input tok | cached | output tok | TTFT s | total s | tok/s | retries |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in results:
        if r.ok:
            cached = f"{r.cached_tokens:,}" if r.cached_tokens is not None else "—"
            ttft = f"{r.ttft_s:.2f}" if r.ttft_s is not None else "—"
            speed = f"{s:.1f}" if (s := r.gen_tok_s) is not None else "—"
            lines.append(f"| {r.index} | {r.input_tokens:,} | {cached} | "
                         f"{r.output_tokens:,} | {ttft} | {r.total_s:.2f} | {speed} | {r.retries} |")
        else:
            lines.append(f"| {r.index} | — | — | — | — | — | failed: {r.error} | {r.retries} |")
    lines.append("")

    os.makedirs(out_dir, exist_ok=True)
    with open(out_path, "w") as f:
        f.write("\n".join(lines))
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", required=True)
    parser.add_argument("--workload", required=True)
    parser.add_argument("--network-note", default="an unspecified network")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    load_env_file()
    provider = load_provider("providers.yaml", args.provider)
    requests = load_workload(args.workload)

    est_input = sum(estimate_tokens(str(r["messages"])) for r in requests)
    output_cap = sum(r.get("max_tokens", 512) for r in requests)
    worst_cost = (est_input * provider.input_per_m + output_cap * provider.output_per_m) / 1e6

    if args.dry_run:
        print(f"[dry-run] provider={provider.name} model={provider.model} base_url={provider.base_url}")
        print(f"[dry-run] workload={args.workload} requests={len(requests)}")
        print(f"[dry-run] est input ~{est_input:,} tok (chars/4 heuristic), "
              f"output cap {output_cap:,} tok")
        print(f"[dry-run] rough cost estimate @ ${provider.input_per_m}/M in + "
              f"${provider.output_per_m}/M out: ~${worst_cost:.4f} "
              f"(NOT a bound: tokenizers vary, and reasoning models may bill "
              f"output beyond max_tokens)")
        print("[dry-run] nothing sent.")
        return

    api_key = os.environ.get(provider.api_key_env)
    if not api_key:
        sys.exit(f"error: {provider.api_key_env} is not set (env or .env)")

    client = OpenAI(base_url=provider.base_url, api_key=api_key,
                    timeout=600, max_retries=0)

    print(f"running {len(requests)} requests against {provider.name} "
          f"({provider.model}), rough cost estimate ~${worst_cost:.2f}")
    results = []
    partial = False
    try:
        for i, req in enumerate(requests, 1):
            r = run_request(client, provider.model, req, i)
            results.append(r)
            if r.ok:
                ttft = f"{r.ttft_s:.2f}s" if r.ttft_s is not None else "?"
                print(f"  [{i}/{len(requests)}] in={r.input_tokens:,} "
                      f"out={r.output_tokens} ttft={ttft} total={r.total_s:.2f}s")
            else:
                print(f"  [{i}/{len(requests)}] FAILED: {r.error}")
    except KeyboardInterrupt:
        partial = True
        print(f"\ninterrupted after {len(results)} requests; writing partial results")

    if not results:
        sys.exit("no requests completed; nothing to write")

    summary = aggregate(results, provider)
    out_path = write_markdown(summary, results, provider, args.workload,
                              "results", args.network_note, partial)
    print(f"\nresults written to {out_path}")
    print(f"  requests: {summary['requests']} ({summary['failed']} failed)")
    print(f"  input/output tokens: {summary['input_tokens']:,} / {summary['output_tokens']:,}")
    if summary["cache_pct"] is not None:
        print(f"  cache hits: {summary['cache_pct']}% of input tokens "
              f"(reported on {summary['cached_count']}/{summary['ok_count']} requests)")
    print(f"  TTFT p50/p95: {fmt_s(summary['p50_ttft'])} / "
          f"{fmt_s(summary['p95_ttft'], summary['p95_ttft_note'])}")
    print(f"  cost: ${summary['list_cost']:.4f} list"
          + (f", ${summary['cache_aware_cost']:.4f} cache-aware"
             if summary["cache_aware_cost"] is not None else ""))


if __name__ == "__main__":
    main()
