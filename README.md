# agent-inference-bench

Chat benchmarks don't tell you what an agent costs to run. An agent resends
the whole conversation every turn, so the prompt grows all session while the
responses stay tiny. Almost all the money goes to input tokens, and most of
those tokens are repeats the provider can serve from cache.

This repo replays the exact request sizes from one of my real coding-agent
sessions against any OpenAI-compatible API and measures speed and cost.
Same provider, same model, same day (Parasail, Qwen3.5-397B):

| | chat (8 requests) | agent session (45 requests) |
|---|---|---|
| input : output tokens | 1 : 9 | 217 : 1 |
| served from cache | 0% | 96.2% |
| time to first token, median | 0.42 s | 1.24 s |
| cost | $0.0075 | $0.92 list, $0.67 after cache discount |

The agent bill is 97% input tokens. Caching covered 96% of them and cut the
bill 28%. First-token latency held around 1.2 s even as the prompt grew from
25k to 56k tokens. For scale: one full day of my agent usage is 437M tokens
in, 1.35M out.

Same session, three models, same day:

| | Qwen3.5-397B | Kimi K2.6 | Qwen3.5-35B |
|---|---|---|---|
| served from cache | 96.2% | 89.0% | 95.7% |
| first token, median / worst | 1.2 / 3.1 s | 1.6 / 12.3 s | 1.2 / 1.4 s |
| cost after cache discount | $0.67 | $1.00 | $0.20 |

Caching behaves the same everywhere, so it's a property of agent traffic,
not of any model. The identical session costs 5x more or less depending on
the model. And Kimi's 12-second worst case is what a cache miss on a
50k-token prompt feels like — an agent loop hits that stall mid-task.

Full per-request reports are in [results/](results/).

## Run it

Needs [uv](https://docs.astral.sh/uv/) and an API key in `.env`
(`PARASAIL_API_KEY=...`).

    uv run run_benchmark.py --provider parasail --workload workloads/chat.jsonl --dry-run
    uv run run_benchmark.py --provider parasail --workload workloads/chat.jsonl
    uv run run_benchmark.py --provider parasail --workload workloads/agent_loop.jsonl

Dry run shows the cost estimate before anything is sent. The agent replay
costs about a dollar. To test another provider, add an entry to
`providers.yaml` with its URL, model, and prices.

## Where the agent workload came from

A real Codex session where the agent hunted down every Rust project on my
machine and ran `cargo clean`. I kept only the per-request token counts and
rebuilt the conversation from a fixed list of 64 filler words, one word per
token, with each request extending the previous one exactly like real agent
traffic does. Nothing from the real session is in this repo, and you don't
have to take my word for it:

    uv run codex_to_workload.py --verify workloads/agent_loop.jsonl
    uv run codex_to_workload.py --verify-shape workloads/agent_loop.jsonl

The first proves the file contains nothing but the 64 filler words — any
digit, symbol, or stray field fails it. The second proves the conversation
grows turn by turn without rewriting history. The live run measured within
2% of the real session's token counts, on two different tokenizers.

To replay your own session: `codex_to_workload.py --list` ranks your local
Codex sessions, then point it at one.

## Honest limits

One run per configuration, one provider, one day, requests sent one at a
time from home wifi. Costs come from the provider's reported token counts,
never my estimates. Worst-case numbers under 20 samples are just the max,
labeled as such. Rate-limited requests are retried with backoff and the
retries are listed in every report. One finding worth keeping: Parasail's
DeepSeek-V4-Flash pool refused about half my requests for hours that day —
that run is committed in results/ too, because reliability is also a number.

MIT licensed.
