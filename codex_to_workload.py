# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Turn a Codex CLI session into a privacy-clean benchmark workload.

Extracts only the session's request shape — per-request (input, output)
token counts — and synthesizes a prefix-stable conversation of filler words
with the same shape. No content from the session survives, provably:

    uv run codex_to_workload.py --list
    uv run codex_to_workload.py <rollout.jsonl> --out workloads/agent_loop.jsonl
    uv run codex_to_workload.py --verify workloads/agent_loop.jsonl
    uv run codex_to_workload.py --verify-shape workloads/agent_loop.jsonl

Sizing is one filler word per token (common words are single tokens under
modern BPE tokenizers); the benchmark reports measured usage, so drift is
visible.
"""

import argparse
import glob
import json
import os
import random
import re
import sys

# Closed vocabulary: --verify checks every word against this list, so leaked
# content is mechanically detectable, not just promised away.
FILLER_WORDS = [
    "river", "carbon", "ladder", "orbit", "meadow", "copper", "signal", "harbor",
    "timber", "violet", "magnet", "canyon", "window", "table", "garden", "bridge",
    "market", "forest", "mountain", "valley", "stone", "cloud", "grass", "field",
    "light", "sound", "paper", "glass", "metal", "plant", "train", "road",
    "house", "water", "earth", "night", "morning", "summer", "winter", "spring",
    "coffee", "bread", "apple", "chair", "door", "floor", "wall", "roof",
    "brick", "sand", "snow", "rain", "wind", "fire", "lake", "ocean",
    "beach", "hill", "path", "gate", "fence", "farm", "corner", "middle",
]
SEED = 7
MIN_DELTA_TOKENS = 16
MAX_OUTPUT_TOKENS = 2048


def iter_rollout_lines(path: str):
    with open(path) as f:
        for line in f:
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def extract_shape(rollout_path: str) -> list[tuple[int, int]]:
    shape = []
    final_total_input = 0
    for item in iter_rollout_lines(rollout_path):
        payload = item.get("payload", {}) or {}
        if payload.get("type") != "token_count":
            continue
        info = payload.get("info") or payload
        last = info.get("last_token_usage") or {}
        input_tokens = last.get("input_tokens", 0)
        output_tokens = last.get("output_tokens", 0)
        if input_tokens > 0:
            shape.append((input_tokens, max(output_tokens, 1)))
        total = info.get("total_token_usage") or {}
        final_total_input = total.get("input_tokens", final_total_input)
    if not shape:
        types_seen = {}
        for item in iter_rollout_lines(rollout_path):
            t = (item.get("payload", {}) or {}).get("type") or item.get("type", "?")
            types_seen[t] = types_seen.get(t, 0) + 1
        sys.exit(f"error: no token_count events in {rollout_path}; "
                 f"line types seen: {types_seen}")
    # sanity: per-request usage must sum to the session's cumulative total
    extracted = sum(s[0] for s in shape)
    if not final_total_input:
        print("shape invariant skipped: rollout carries no cumulative total")
    elif abs(extracted - final_total_input) > 0.01 * final_total_input:
        sys.exit(f"error: extracted per-request input ({extracted:,}) does not "
                 f"match the session's cumulative total ({final_total_input:,}); "
                 f"this rollout's schema differs from what this tool understands")
    else:
        print(f"shape invariant ok: per-request sum {extracted:,} == "
              f"session total {final_total_input:,}")
    return shape


def filler_text(rng: random.Random, target_tokens: int) -> str:
    return " ".join(rng.choice(FILLER_WORDS) for _ in range(max(target_tokens, 1)))


def synthesize(shape: list[tuple[int, int]]) -> tuple[list[dict], int, int]:
    """Prefix-stable requests matching the shape: each request extends the
    previous one verbatim, so prefix caching gets exercised like the real
    session. An input-size drop (context compaction) starts a fresh segment.
    Segments open with system + a small user message because endpoints
    reject conversations with no user turn."""
    rng = random.Random(SEED)

    def open_segment(input_tokens: int) -> tuple[list[dict], int]:
        user_tokens = min(MIN_DELTA_TOKENS, max(input_tokens - 1, 1))
        system_tokens = max(input_tokens - user_tokens, 1)
        msgs = [{"role": "system", "content": filler_text(rng, system_tokens)},
                {"role": "user", "content": filler_text(rng, user_tokens)}]
        return msgs, system_tokens + user_tokens

    messages, emitted = open_segment(shape[0][0])
    emitted_peak = emitted
    segments = 1
    requests = []
    for i, (input_tokens, output_tokens) in enumerate(shape):
        if i > 0:
            delta = input_tokens - emitted
            if delta < 0:
                segments += 1
                messages, emitted = open_segment(input_tokens)
            else:
                step = max(delta, MIN_DELTA_TOKENS)
                messages.append({"role": "user", "content": filler_text(rng, step)})
                emitted += step
        emitted_peak = max(emitted_peak, emitted)
        requests.append({
            "messages": [dict(m) for m in messages],
            "max_tokens": min(max(output_tokens, 1), MAX_OUTPUT_TOKENS),
        })
    return requests, segments, emitted_peak


def list_sessions() -> None:
    root = os.path.expanduser("~/.codex/sessions")
    rows = []
    for path in glob.glob(os.path.join(root, "*/*/*/rollout-*.jsonl")):
        requests = calls = 0
        cumulative_in = peak_in = 0
        try:
            for item in iter_rollout_lines(path):
                payload = item.get("payload", {}) or {}
                payload_type = payload.get("type", "")
                if payload_type == "function_call":
                    calls += 1
                elif payload_type == "token_count":
                    requests += 1
                    info = payload.get("info") or payload
                    last = info.get("last_token_usage") or {}
                    peak_in = max(peak_in, last.get("input_tokens", 0))
                    total = info.get("total_token_usage") or {}
                    cumulative_in = total.get("input_tokens", cumulative_in)
        except OSError:
            continue
        if requests:
            rows.append((os.path.relpath(path, root),
                         requests, calls, peak_in, cumulative_in))
    rows.sort(key=lambda r: -r[4])
    print(f"{'session':<72} {'reqs':>5} {'calls':>6} {'peak_in':>9} {'cum_in':>13}")
    for rel, requests, calls, peak, cumulative in rows[:25]:
        print(f"{rel:<72} {requests:>5} {calls:>6} {peak:>9,} {cumulative:>13,}")
    print(f"\n{len(rows)} sessions total. Good replay candidates: 20-80 reqs, "
          f"peak_in 15k-60k, a task you can describe publicly.")


CONTENT_PATTERN = re.compile(r"[a-z ]+\Z")


def verify(workload_path: str) -> bool:
    """Exact schema, exact charset, closed vocabulary. Digits, punctuation,
    non-ASCII, extra fields, and non-integer max_tokens all fail."""
    allowed = set(FILLER_WORDS)
    problems = []
    requests = 0
    max_input_words = 0

    with open(workload_path) as f:
        for line_number, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                request = json.loads(line)
            except json.JSONDecodeError as e:
                problems.append((line_number, f"invalid JSON: {e}"))
                continue
            requests += 1
            if not isinstance(request, dict):
                problems.append((line_number, f"not a JSON object: {type(request).__name__}"))
                continue
            if set(request) != {"messages", "max_tokens"}:
                problems.append((line_number, f"unexpected top-level keys: {sorted(request)}"))
                continue
            if not isinstance(request["max_tokens"], int):
                problems.append((line_number, f"max_tokens is not an integer: "
                                              f"{request['max_tokens']!r}"))
            messages = request["messages"]
            if not isinstance(messages, list) or not messages:
                problems.append((line_number, "messages is not a non-empty list"))
                continue
            words_in_request = 0
            for message in messages:
                if not isinstance(message, dict) or set(message) != {"role", "content"}:
                    problems.append((line_number, f"unexpected message keys: "
                                     f"{sorted(message) if isinstance(message, dict) else type(message).__name__}"))
                    continue
                if message["role"] not in ("system", "user"):
                    problems.append((line_number, f"unexpected role: {message['role']!r}"))
                content = message["content"]
                if not isinstance(content, str) or not content:
                    problems.append((line_number, "content is not a non-empty string"))
                    continue
                if not CONTENT_PATTERN.fullmatch(content):
                    bad_chars = sorted(set(re.sub(r"[a-z ]", "", content)))[:10]
                    problems.append((line_number, f"content contains characters outside "
                                                  f"[a-z ]: {bad_chars}"))
                for word in content.split():
                    if word not in allowed:
                        problems.append((line_number, f"foreign word: {word!r}"))
                words_in_request += len(content.split())
            max_input_words = max(max_input_words, words_in_request)

    if problems:
        print(f"PRIVACY CHECK FAILED: {len(problems)} problems found")
        for line_number, what in problems[:20]:
            print(f"  line {line_number}: {what}")
        return False
    print(f"PRIVACY CHECK PASSED: {requests} requests, vocabulary closed "
          f"({len(FILLER_WORDS)} words), schema exact, charset [a-z ] only, "
          f"max prompt ~{max_input_words:,} words (~tokens)")
    return True


def verify_shape(workload_path: str) -> bool:
    """Each request must extend the previous one verbatim with one user turn;
    a fresh system+user pair marks a compaction boundary."""
    previous = None
    segments = 0
    requests = 0
    with open(workload_path) as f:
        for line_number, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            messages = json.loads(line)["messages"]
            requests += 1
            is_segment_open = (len(messages) == 2 and
                               messages[0]["role"] == "system" and
                               messages[1]["role"] == "user")
            if previous is None:
                segments += 1
            elif messages[:len(previous)] == previous and len(messages) == len(previous) + 1:
                pass
            elif is_segment_open and messages != previous:
                segments += 1
            else:
                print(f"SHAPE CHECK FAILED: line {line_number} neither extends "
                      f"the previous request nor opens a fresh segment")
                return False
            previous = messages
    print(f"SHAPE CHECK PASSED: {requests} requests, prefix-stable, "
          f"{segments} conversation segment(s)")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rollout", nargs="?")
    parser.add_argument("--out", default="workloads/agent_loop.jsonl")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--verify", metavar="WORKLOAD")
    parser.add_argument("--verify-shape", metavar="WORKLOAD")
    args = parser.parse_args()

    if args.list:
        list_sessions()
        return
    if args.verify:
        sys.exit(0 if verify(args.verify) else 1)
    if args.verify_shape:
        sys.exit(0 if verify_shape(args.verify_shape) else 1)
    if not args.rollout:
        parser.error("provide a rollout file, --list, --verify, or --verify-shape")

    shape = extract_shape(os.path.expanduser(args.rollout))
    print(f"extracted shape: {len(shape)} requests")
    print(f"{'req':>4} {'input_tok':>10} {'output_tok':>10}")
    for i, (input_tokens, output_tokens) in enumerate(shape, 1):
        print(f"{i:>4} {input_tokens:>10,} {output_tokens:>10,}")
    total_in = sum(s[0] for s in shape)
    total_out = sum(s[1] for s in shape)
    print(f"shape totals: {total_in:,} input tok, {total_out:,} output tok, "
          f"peak prompt {max(s[0] for s in shape):,} tok")

    requests, segments, emitted_peak = synthesize(shape)
    emitted_total = sum(
        sum(len(m["content"].split()) for m in r["messages"]) for r in requests
    )
    print(f"emitted totals: {emitted_total:,} input words (~tokens), "
          f"emitted peak prompt {emitted_peak:,} words (~tokens), "
          f"{segments} conversation segment(s)")
    if segments > 1:
        print(f"note: the source session compacted its context {segments - 1} "
              f"time(s); the workload breaks the prefix cache exactly there")

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w") as f:
        for request in requests:
            f.write(json.dumps(request) + "\n")
    size_mb = os.path.getsize(args.out) / 1e6
    print(f"\nwrote {len(requests)} requests to {args.out} ({size_mb:.1f} MB)")
    print(f"check it: uv run codex_to_workload.py --verify {args.out} && "
          f"uv run codex_to_workload.py --verify-shape {args.out}")


if __name__ == "__main__":
    main()
