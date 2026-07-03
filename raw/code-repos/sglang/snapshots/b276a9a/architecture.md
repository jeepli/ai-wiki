---
repo: sglang
commit: b276a9acee8a02159a9a8d839da8a7b4dd898b58
source_version: b276a9a
document: architecture.md
status: source-backed
---

# Architecture

Source snapshot: `sglang` commit
`b276a9acee8a02159a9a8d839da8a7b4dd898b58`.

## Boundary Model

SGLang has two major Python-facing layers. The frontend language layer exports
programming primitives such as `function`, `gen`, `select`, `system`, `user`,
`assistant`, `image`, `video`, `Runtime`, and backend selectors from
`python/sglang/__init__.py` and `python/sglang/lang/api.py`
(`sglang@b276a9a:python/sglang/__init__.py`). The runtime layer is SRT, exposed
through lazy `ServerArgs` and `Engine` imports and implemented under
`python/sglang/srt/`.

The package initializer also installs macOS/MPS compatibility stubs when needed
and applies Hugging Face transformer patches before exporting APIs
(`sglang@b276a9a:python/sglang/__init__.py`).

## Server and Process Boundary

`python/sglang/srt/entrypoints/http_server.py` is the main HTTP server entrypoint.
It declares itself as the SRT inference server entrypoint, imports FastAPI,
OpenAI/Anthropic/Ollama protocol handlers, `Engine`, tokenizer manager
initialization, scheduler/detokenizer process runners, request IO structs, and
server args (`sglang@b276a9a:python/sglang/srt/entrypoints/http_server.py`).

Global server state stores tokenizer manager, template manager, and scheduler
info in `_GlobalState`, with setters/getters in the same file. This makes the
server file the first place to inspect for HTTP lifecycle and runtime process
wiring (`sglang@b276a9a:python/sglang/srt/entrypoints/http_server.py#_GlobalState`).

## Scheduler and Runtime Managers

`python/sglang/srt/managers/scheduler.py#Scheduler` manages a tensor-parallel
GPU worker. Its imports show the ownership boundary: request IO structs,
schedule batches, schedule policies, grammar manager, disaggregation queues,
LoRA loaders, HiSparse coordinator, memory/cache helpers, model config, model
runner, metrics/reporting components, and IPC channels
(`sglang@b276a9a:python/sglang/srt/managers/scheduler.py#Scheduler`).

`ScheduleBatch` groups runtime requests for execution, and `SchedulePolicy` /
`PrefillAdder` control request admission and prefill decisions
(`sglang@b276a9a:python/sglang/srt/managers/schedule_batch.py#ScheduleBatch`,
`sglang@b276a9a:python/sglang/srt/managers/schedule_policy.py`).

## Cache, Model, and Kernel Layers

- Prefix/KV cache: `RadixCache`, `RadixCacheCpp`, memory pools, chunk cache,
  HiCache, SWA cache, Mamba cache, and unified cache live under
  `python/sglang/srt/mem_cache/`.
- Model execution: `ModelRunner`, `ModelRunnerOutput`, and
  `ModelRunnerKVCacheMixin` are defined in `python/sglang/srt/model_executor/`.
- Native kernels: `sgl-kernel/csrc/` and `sgl-kernel/include/` expose kernel ops
  and torch extension surfaces used by SRT layers and model execution.

## Dependency Notes

`python/pyproject.toml` declares runtime dependencies on major serving and kernel
packages, including `flash-attn-4`, `flashinfer_python[cu13]`,
`flashinfer_cubin`, `sglang-kernel`, CUTLASS DSL, Torch 2.11, transformers,
FastAPI, uvicorn, uvloop, xgrammar, outlines-related packages, and tracing
extras (`sglang@b276a9a:python/pyproject.toml`).
