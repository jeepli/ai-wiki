# vLLM

**Summary**: vLLM is an inference and serving engine with offline inference, OpenAI-compatible serving, V1 engine runtime, scheduling, paged KV cache management, attention backend selection, distributed execution, and native kernels. (source: raw/code-repos/vllm/snapshots/8357226/overview.md)

**Sources**: `raw/code-repos/vllm/latest.yml`; `raw/code-repos/vllm/snapshots/8357226/overview.md`; `raw/code-repos/vllm/snapshots/8357226/architecture.md`; `raw/code-repos/vllm/snapshots/8357226/key-flows.md`; `raw/code-repos/vllm/snapshots/8357226/api-surface.md`; `raw/code-repos/vllm/snapshots/8357226/build-and-entrypoints.md`

**Last updated**: 2026-07-03

---

## Why it matters

vLLM is a full serving system rather than only a kernel package: it connects user entrypoints, OpenAI-compatible HTTP serving, asynchronous engine clients, scheduler logic, KV cache management, worker execution, attention backend selection, and native kernels. (source: raw/code-repos/vllm/snapshots/8357226/overview.md; raw/code-repos/vllm/snapshots/8357226/architecture.md)

It is a useful anchor for studying how [[models/transformer]] inference becomes a production-style service: requests enter through API or offline interfaces, then move through tokenization/input processing, scheduling, KV-cache allocation, worker execution, and output processing. (source: raw/code-repos/vllm/snapshots/8357226/key-flows.md)

## Key ideas

The public Python surface lazily exports `LLM`, engine argument classes, engine classes, sampling/pooling params, prompt types, output types, `ModelRegistry`, and Ray initialization helpers. (source: raw/code-repos/vllm/snapshots/8357226/api-surface.md)

Online serving starts in `vllm/entrypoints/openai/api_server.py`: `build_app(...)` creates the FastAPI application and registers serving routers, while `build_async_engine_client(...)` and `build_async_engine_client_from_engine_args(...)` construct the engine client from CLI/server arguments. (source: raw/code-repos/vllm/snapshots/8357226/key-flows.md)

The V1 runtime centers on `AsyncLLM`, `EngineCore`, `Scheduler`, `KVCacheManager`, and GPU model runner classes. (source: raw/code-repos/vllm/snapshots/8357226/architecture.md)

## Method or mechanism

`AsyncLLM` converts incoming engine inputs to `EngineCoreRequest` objects through `InputProcessor`, converts engine outputs to `RequestOutput` objects through `OutputProcessor`, and talks to the background engine through `EngineCoreClient.make_async_mp_client`. (source: raw/code-repos/vllm/snapshots/8357226/key-flows.md)

`Scheduler` owns request admission, waiting/skipped/running queues, scheduling policy, maximum running request limits, maximum scheduled token limits, KV connector hooks, encoder/multimodal cache managers, and finished-request tracking. (source: raw/code-repos/vllm/snapshots/8357226/architecture.md; raw/code-repos/vllm/snapshots/8357226/key-flows.md)

`KVCacheManager` hides KV-cache block internals from the scheduler with `KVCacheBlocks`, tracks block-pool usage, and performs prefix-cache lookup through `get_computed_blocks`. (source: raw/code-repos/vllm/snapshots/8357226/architecture.md; raw/code-repos/vllm/snapshots/8357226/key-flows.md)

The attention layer includes backend selection and implementations for FlashAttention, FlashInfer, Triton, ROCm/AITER, CPU, Mamba/linear attention, FlexAttention, and related attention ops. (source: raw/code-repos/vllm/snapshots/8357226/architecture.md; raw/code-repos/vllm/snapshots/8357226/key-flows.md)

## Results and limitations

This wiki source captures the structure of commit `8357226`, but it does not validate throughput, latency, memory use, or correctness for a specific model or deployment configuration. (source: raw/code-repos/vllm/snapshots/8357226/manifest.yml; raw/code-repos/vllm/snapshots/8357226/build-and-entrypoints.md)

The main learning limitation is that vLLM has several layers with similar names: public `LLM`, legacy engine exports, V1 `AsyncLLM`, `EngineCore`, scheduler, and workers should be kept separate when tracing implementation questions. (source: raw/code-repos/vllm/snapshots/8357226/api-surface.md; raw/code-repos/vllm/snapshots/8357226/architecture.md)

## Open questions

Runtime decisions such as backend selection, distributed execution mode, KV offload, and scheduler behavior should be answered from the exact code path and configuration in use, preferably with CodeGraph or Serena over the checked-out repo. (source: raw/code-repos/vllm/snapshots/8357226/architecture.md)

## Related pages

- [[concepts/kv-cache]]
- [[systems/flashattention]]
- [[systems/flashinfer]]
- [[systems/sglang]]
- [[models/transformer]]
