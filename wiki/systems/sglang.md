# SGLang

**Summary**: SGLang is an inference engine and structured generation framework with a frontend language API, SGLang Runtime, OpenAI-compatible serving, scheduler, radix/prefix cache, model execution, disaggregation, and the companion `sgl-kernel` package. (source: raw/code-repos/sglang/snapshots/b276a9a/overview.md)

**Sources**: `raw/code-repos/sglang/latest.yml`; `raw/code-repos/sglang/snapshots/b276a9a/overview.md`; `raw/code-repos/sglang/snapshots/b276a9a/architecture.md`; `raw/code-repos/sglang/snapshots/b276a9a/key-flows.md`; `raw/code-repos/sglang/snapshots/b276a9a/api-surface.md`; `raw/code-repos/sglang/snapshots/b276a9a/build-and-entrypoints.md`

**Last updated**: 2026-07-03

---

## Why it matters

SGLang is useful to study as both a programming interface for structured generation and a serving runtime for large language and vision-language models. (source: raw/code-repos/sglang/snapshots/b276a9a/overview.md; raw/code-repos/sglang/snapshots/b276a9a/architecture.md)

It exposes frontend primitives such as `function`, `gen`, `select`, role helpers, media helpers, runtime backends, and lazy engine APIs, while the SRT runtime handles HTTP serving, scheduling, model execution, cache management, constrained decoding, function calling, and native kernels. (source: raw/code-repos/sglang/snapshots/b276a9a/overview.md; raw/code-repos/sglang/snapshots/b276a9a/api-surface.md)

## Key ideas

SGLang has two main Python-facing layers: the frontend language layer under `python/sglang/lang/`, and the SGLang Runtime under `python/sglang/srt/`. (source: raw/code-repos/sglang/snapshots/b276a9a/architecture.md)

The SRT HTTP server lives in `python/sglang/srt/entrypoints/http_server.py`, imports FastAPI and serving adapters, wires `Engine`, tokenizer manager initialization, scheduler/detokenizer process runners, request IO structs, and server args, and stores tokenizer/template/scheduler state in `_GlobalState`. (source: raw/code-repos/sglang/snapshots/b276a9a/architecture.md; raw/code-repos/sglang/snapshots/b276a9a/key-flows.md)

The scheduler is a tensor-parallel GPU worker manager that coordinates request IO structs, schedule batches, schedule policies, grammar manager, disaggregation queues, LoRA loaders, cache helpers, model config, model runner, metrics/reporting, and IPC channels. (source: raw/code-repos/sglang/snapshots/b276a9a/architecture.md)

## Method or mechanism

CLI startup begins at the `sglang` console script, which maps to `sglang.cli.main:main`; the CLI dispatches `serve`, `generate`, and `version`, and the serve path enters the SRT HTTP server. (source: raw/code-repos/sglang/snapshots/b276a9a/key-flows.md; raw/code-repos/sglang/snapshots/b276a9a/build-and-entrypoints.md)

Runtime requests use IO structs such as generate, embedding, tokenize, LoRA, profile, weight update, session, and memory management requests before routing through tokenizer/template managers into scheduler and model execution. (source: raw/code-repos/sglang/snapshots/b276a9a/key-flows.md)

Prefix/KV caching is centered on `RadixCache` and `RadixCacheCpp`, with related chunk cache, SWA radix cache, Mamba radix cache, unified radix cache, HiCache storage, and memory pools under `python/sglang/srt/mem_cache/`. (source: raw/code-repos/sglang/snapshots/b276a9a/key-flows.md; raw/code-repos/sglang/snapshots/b276a9a/architecture.md)

The companion `sgl-kernel` package exposes C++/CUDA/ROCm/MUSA/Metal sources, operation headers, Python bindings, benchmarks, and tests for native kernel functionality. (source: raw/code-repos/sglang/snapshots/b276a9a/overview.md; raw/code-repos/sglang/snapshots/b276a9a/key-flows.md)

## Results and limitations

This wiki source captures structure for commit `b276a9a`, but it does not measure model throughput, scheduler behavior, radix-cache hit rate, or kernel performance. (source: raw/code-repos/sglang/snapshots/b276a9a/manifest.yml; raw/code-repos/sglang/snapshots/b276a9a/build-and-entrypoints.md)

The main learning limitation is scope: SGLang includes frontend language APIs, SRT serving internals, model execution, constrained decoding, disaggregation, and native kernels, so implementation questions should start from the exact subsystem rather than the repo root. (source: raw/code-repos/sglang/snapshots/b276a9a/overview.md; raw/code-repos/sglang/snapshots/b276a9a/api-surface.md)

## Open questions

When comparing SGLang with [[systems/vllm]], use the exact checked-out code snapshots and trace concrete request, scheduling, and cache flows instead of relying on high-level project descriptions. (source: raw/code-repos/sglang/snapshots/b276a9a/key-flows.md; raw/code-repos/vllm/snapshots/8357226/key-flows.md)

## Related pages

- [[concepts/kv-cache]]
- [[systems/vllm]]
- [[systems/flashinfer]]
- [[systems/flashattention]]
- [[models/transformer]]
