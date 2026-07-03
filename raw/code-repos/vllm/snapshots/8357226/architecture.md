---
repo: vllm
commit: 8357226f4f1b92aa2139ebc482ca71012f02016b
source_version: 8357226
document: architecture.md
status: source-backed
---

# Architecture

Source snapshot: `vllm` commit
`8357226f4f1b92aa2139ebc482ca71012f02016b`.

## Boundary Model

vLLM separates user/API surfaces from the runtime engine. `vllm/__init__.py`
uses lazy imports for public classes and output/config types so importing the
package does not eagerly load the full engine stack
(`vllm@8357226:vllm/__init__.py`). Offline users typically start at
`vllm/entrypoints/llm.py#LLM`, while online serving starts at
`vllm/entrypoints/openai/api_server.py`.

The OpenAI server constructs an `AsyncEngineArgs` from CLI/server arguments,
creates a `VllmConfig`, then instantiates `vllm.v1.engine.async_llm.AsyncLLM`
(`vllm@8357226:vllm/entrypoints/openai/api_server.py#build_async_engine_client`,
`vllm@8357226:vllm/entrypoints/openai/api_server.py#build_async_engine_client_from_engine_args`).

## V1 Runtime Components

- `AsyncLLM` is the asynchronous engine client. It owns an input processor,
  output processor, renderer/tokenizer access, metrics/logging, and an
  `EngineCoreClient` created by `EngineCoreClient.make_async_mp_client`
  (`vllm@8357226:vllm/v1/engine/async_llm.py#AsyncLLM`).
- `EngineCore` is the core execution loop abstraction
  (`vllm@8357226:vllm/v1/engine/core.py#EngineCore`). Related process and actor
  variants live in the same file (`EngineCoreProc`, `EngineCoreActor`).
- `Scheduler` owns request admission, waiting/running queues, scheduling policy,
  max sequence/token constraints, KV connector integration, encoder/multimodal
  budgets, and finished-request tracking
  (`vllm@8357226:vllm/v1/core/sched/scheduler.py#Scheduler`).
- `KVCacheManager` hides KV-cache internal data structures from the scheduler
  through `KVCacheBlocks`, tracks block-pool usage, and performs prefix-cache
  lookup via `get_computed_blocks`
  (`vllm@8357226:vllm/v1/core/kv_cache_manager.py#KVCacheManager`,
  `vllm@8357226:vllm/v1/core/kv_cache_manager.py#KVCacheBlocks`).
- Worker/model runner classes execute batches on hardware backends
  (`vllm@8357226:vllm/v1/worker/gpu_model_runner.py#GPUModelRunner`,
  `vllm@8357226:vllm/v1/worker/gpu/model_runner.py#GPUModelRunner`).

## Attention and Kernel Layer

The V1 attention package contains backend selection and backend-specific
implementations for FlashAttention, FlashInfer, Triton, ROCm/AITER, CPU,
Mamba/linear attention, and related ops
(`vllm@8357226:vllm/v1/attention/backends/registry.py`,
`vllm@8357226:vllm/v1/attention/backends/flashinfer.py`,
`vllm@8357226:vllm/v1/attention/backends/flash_attn.py`). Native kernels and
torch bindings live under `csrc/`, with separate CPU, libtorch-stable, ROCm,
MoE, quantization, and attention areas.

## Configuration and Plugins

`pyproject.toml` declares the console script `vllm =
vllm.entrypoints.cli.main:main` and plugin entry points for LoRA resolvers
(`vllm@8357226:pyproject.toml`). Public runtime/config objects are exposed via
`vllm/__init__.py`, while detailed configuration modules live under
`vllm/config/`.
