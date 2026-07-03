---
repo: vllm
commit: 8357226f4f1b92aa2139ebc482ca71012f02016b
source_version: 8357226
document: overview.md
status: source-backed
---

# Overview

vLLM is tracked here as an inference-engine source snapshot for LLM serving,
offline inference, scheduling, paged KV cache, attention backend selection,
distributed execution, and custom kernels. Source: `vllm` commit
`8357226f4f1b92aa2139ebc482ca71012f02016b`; declared role in `code-repos.yml`;
package metadata in `external-repos/vllm/pyproject.toml`.

## Directory Map

- `vllm/entrypoints/` contains user-facing entrypoints: offline `LLM`,
  OpenAI-compatible server, CLI, generate/pooling/speech-to-text routes, gRPC,
  and serving helpers (`vllm@8357226:vllm/entrypoints/llm.py`,
  `vllm@8357226:vllm/entrypoints/openai/api_server.py`).
- `vllm/v1/` is the V1 runtime area. It includes `engine/`, `core/sched/`,
  `core/kv_cache_manager.py`, `executor/`, `worker/`, `attention/`,
  `structured_output/`, `sample/`, `spec_decode/`, and KV offload components
  (`vllm@8357226:vllm/v1/engine/async_llm.py`,
  `vllm@8357226:vllm/v1/core/sched/scheduler.py`).
- `vllm/model_executor/` and `vllm/models/` contain model loading/execution
  support outside the V1 worker package.
- `csrc/` contains native kernels and bindings for attention, CPU attention,
  quantization, MoE, quickreduce, custom allocators, and torch bindings
  (`vllm@8357226:csrc/torch_bindings.cpp`, `vllm@8357226:csrc/cpu/cpu_attn.cpp`).
- `rust/` contains Rust crates/protos used by vLLM infrastructure, including
  chat/parser/tokenizer-related components.
- `tests/`, `benchmarks/`, `examples/`, and `docs/` provide validation, perf,
  usage examples, and design documentation.

## Main Subsystems

- Public Python API: `vllm/__init__.py` lazily exposes `LLM`, `EngineArgs`,
  `AsyncLLMEngine`, `LLMEngine`, `SamplingParams`, output types, and model
  registry objects.
- Online serving: `vllm/entrypoints/openai/api_server.py` builds a FastAPI app,
  registers serve/OpenAI/model/SageMaker/generate routers, and constructs
  `AsyncLLM` through `AsyncEngineArgs`.
- V1 engine: `vllm/v1/engine/async_llm.py` wraps input processing,
  output processing, an `EngineCoreClient`, and metrics/logging.
- Scheduling/KV cache: `vllm/v1/core/sched/scheduler.py#Scheduler` owns
  request queues and scheduling constraints, while
  `vllm/v1/core/kv_cache_manager.py#KVCacheManager` owns KV block allocation,
  prefix cache lookup, and block-pool usage.
- Worker/model execution: `vllm/v1/worker/gpu_model_runner.py#GPUModelRunner`
  and `vllm/v1/worker/gpu/model_runner.py#GPUModelRunner` are primary GPU
  model-runner inspection points.
